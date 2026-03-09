import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common"))
from agent_base import BaseAgent

class DesignerAgent(BaseAgent):
    def __init__(self):
        config_path = Path(__file__).parent.parent / "config.yaml"
        super().__init__(config_path)
        self.display_name = "Дизайнер"

    # --- Инструменты ---
    async def generate_component(self, **kwargs) -> str:
        """
        Генерирует HTML/CSS для UI-компонента.
        Принимает параметры: component_type (или type), style, color_scheme.
        """
        # Извлекаем component_type из возможных вариантов
        component_type = kwargs.get('component_type') or kwargs.get('type')
        style = kwargs.get('style', 'modern')
        color_scheme = kwargs.get('color_scheme', 'light')

        if not component_type:
            return json.dumps({"error": "Не указан тип компонента (component_type или type)"})

        return json.dumps({
            "status": "ok",
            "message": f"Генерация компонента '{component_type}' в стиле {style}",
            "component_type": component_type,
            "style": style,
            "color_scheme": color_scheme
        })

    async def generate_page(self, description: str, style: str = "modern", responsive: bool = True) -> str:
        """Возвращает код страницы (заглушка)."""
        return json.dumps({
            "status": "ok",
            "message": f"Генерация страницы: {description[:50]}...",
            "description": description,
            "style": style,
            "responsive": responsive
        })

    async def generate_css(self, description: str, framework: str = "css") -> str:
        """Возвращает CSS (заглушка)."""
        return json.dumps({
            "status": "ok",
            "message": f"Генерация {framework} для: {description[:50]}...",
            "description": description,
            "framework": framework
        })

    async def analyze_screenshot(self, image_url: str = "") -> str:
        """Заглушка для будущего функционала."""
        return json.dumps({
            "status": "info",
            "message": "Анализ скриншотов пока не реализован. В будущем я смогу генерировать код по изображению."
        })