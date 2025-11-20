from flask import Blueprint
from app.api.endpoints.teachers import teachers_bp
from app.api.endpoints.groups import groups_bp
from app.api.endpoints.rooms import rooms_bp
from app.api.endpoints.subjects import subjects_bp
from app.api.endpoints.schedules import schedules_bp
from app.api.endpoints.semesters import semesters_bp

# Создаем главный Blueprint API
api_bp = Blueprint('api', __name__)

# Регистрируем все дочерние Blueprint'ы
# Обрати внимание: префикс URL будет суммироваться с префиксом api_bp (/api)
# Так как в дочерних блюпринтах мы уже писали полные пути (например /teachers),
# то здесь просто регистрируем их без дополнительного url_prefix, 
# либо нужно убрать слеши в дочерних файлах.
#
# ВАРИАНТ: Оставить пути в дочерних файлах как есть, и здесь просто зарегистрировать их.
# Но Flask требует уникальных имен для блюпринтов.

def register_endpoints(app):
    """Функция для регистрации блюпринтов в приложении (вызывается в create_app)"""
    # Этот метод устарел, если мы используем вложенные блюпринты.
    # Лучше просто зарегистрировать их в api_bp
    pass

# Регистрируем дочерние блюпринты в главном
api_bp.register_blueprint(teachers_bp)
api_bp.register_blueprint(groups_bp)
api_bp.register_blueprint(rooms_bp)
api_bp.register_blueprint(subjects_bp)
api_bp.register_blueprint(schedules_bp)
api_bp.register_blueprint(semesters_bp)