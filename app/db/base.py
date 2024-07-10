# app/db/base.py

from app.db.base_class import Base  # Import the Base class
from app.db.models.questions import Question
from app.db.models.users import User
from app.db.models.chats import Chat
from app.db.models.messages import Message
from app.db.models.domains import Domain
from app.db.models.issues import Issue
from app.db.models.urlTrain import urltrain