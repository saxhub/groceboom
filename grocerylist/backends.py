from django.contrib.auth.backends import ModelBackend
import logging
log = logging.getLogger(__name__)

class PerObjectBackend(ModelBackend):

    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_active:
            return False
        if perm in self.get_all_permissions(user_obj):
	
	        if 'own' in perm:
	        	if obj.owner.id == user_obj.id:
	        		return True

	        else:
	        	return True


