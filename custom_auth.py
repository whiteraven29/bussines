from django.contrib.auth.backends import BaseBackend
from manager.models import Manager
from worker.models import Worker
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

class CustomUserAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        logger.debug(f"CustomUserAuthBackend authenticate called with username={username}")
        print(f"CustomUserAuthBackend authenticate called with username={username}")
        if username is None or password is None:
            logger.debug("Username or password is None")
            return None

        try:
            manager_user = Manager.objects.get(username=username)
            if manager_user.check_password(password):
                logger.debug("Manager user authenticated successfully")
                return manager_user
            else:
                logger.debug("Manager password mismatch")
                return None
        except Manager.DoesNotExist:
            logger.debug("Manager user does not exist")
        except Exception as e:
            logger.error(f"Error while authenticating manager user: {e}")

        try:
            worker_user = Worker.objects.get(username=username)
            if worker_user.check_password(password):
                logger.debug("Worker user authenticated successfully")
                return worker_user
            else:
                logger.debug("Worker password mismatch")
                return None
        except Worker.DoesNotExist:
            logger.debug("Worker user does not exist")
        except Exception as e:
            logger.error(f"Error while authenticating worker user: {e}")

        logger.debug("User does not exist in any user model")
        return None

    def get_user(self, user_id):
        try:
            return Manager.objects.get(pk=user_id)
        except Manager.DoesNotExist:
            try:
                return Worker.objects.get(pk=user_id)
            except Worker.DoesNotExist:
                return None
