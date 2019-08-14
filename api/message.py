import json
import queue

import flask
from connexion import NoContent
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound


from orm import db, Message, Application, Priority

connected = []

# Using connexion automatic routing
# paths:
#  /:
#    get:
#       # Implied operationId: api.get
#  /foo:
#    get:
#       # Implied operationId: api.foo.search
#    post:
#       # Implied operationId: api.foo.post
#
#  '/foo/{id}':
#    get:
#       # Implied operationId: api.foo.get
#    put:
#       # Implied operationId: api.foo.put
#    copy:
#       # Implied operationId: api.foo.copy
#    delete:
#       # Implied operationId: api.foo.delete


def find_connected_client(app):
    for sse_client in connected:
        if sse_client.client.id is app.client.id:
            return sse_client
    flask.current_app.logger.debug("Client %i not connected", app.client.id)
    return None


def post(body):
    try:
        routing_token = body["token"]
    except KeyError:
        return NoContent, 400
    try:
        app = Application.query.filter_by(routing_token=routing_token).one()
    except NoResultFound:
        return NoContent, 400
    try:
        data = body["data"]
    except KeyError:
        return NoContent, 400
    try:
        priority = Priority(body["priority"])
    except KeyError:
        priority = Priority.NORMAL
    try:
        time_to_live = body["time_to_live"]
    except KeyError:
        time_to_live = "2419200"
    try:
        collapse_key = body["collapse_key"]
    except KeyError:
        collapse_key = None
    message = Message(
        data=str(data),
        priority=priority,
        time_to_live=time_to_live,
        collapse_key=collapse_key,
        target=app,
    )
    try:
        db.session.add(message)
        db.session.commit()
    except SQLAlchemyError as e:
        print(str(e))
        return NoContent, 400
    sse_client = find_connected_client(app)
    if sse_client:
        sse_client.send(message.id)
    return NoContent, 200


def subscribe(user):
    client = user
    for sse_client in connected:
        if sse_client.client.id is client.id:
            sse_client.send(SSEClient.END_STREAM)
    sse_client = SSEClient(client)
    for m in (
        db.session.query(Message)
        .join(Message.target, Application.client)
        .filter(Application.client == client)
        .order_by(Message.timestamp)
        .all()
    ):
        sse_client.send(m.id)
    connected.append(sse_client)
    return flask.Response(
        flask.helpers.stream_with_context(sse_client.generator()),
        content_type="text/event-stream",
    )


class SSEClient:
    END_STREAM = {}

    def __init__(self, client):
        self.client = client
        self.queue = queue.Queue()

    def send(self, messageid):
        self.queue.put(messageid)

    def generator(self):
        # make sure headers are sent immediately to the client
        yield ""
        try:
            while True:
                msgid = self.queue.get()
                if msgid == self.END_STREAM:
                    break
                lastmsg = json.dumps(Message.query.get(msgid).as_dict())
                db.session.close()
                yield "data: " + lastmsg + "\n\n"
                # This is somehow necessary for detecting that the client disconnected
                # before the next message
                yield ""
                # If we reached this point the message has been delivered to the
                # connected client successfully.
                # So we can remove it from the db at this point
                flask.current_app.logger.info(
                    "message %i delivered, deleting from db", msgid
                )
                # Deleting the message from the db needs to be done in a seperate
                # SQLAlchemy session here because the generator runs on different
                # threads and session sharing across threads is apparently not good.
                session_factory = db.sessionmaker(bind=db.get_engine(db.get_app()))
                session = session_factory()
                try:
                    session.delete(session.query(Message).get(msgid))
                    session.commit()
                except SQLAlchemyError:
                    pass
                finally:
                    session.close()

        except SQLAlchemyError as e:
            print(str(e))
        finally:
            try:
                connected.remove(self)
            except ValueError:
                # it's okay, we just want it gone.
                pass
            flask.current_app.logger.info("Client %i disconnected.", self.client.id)
