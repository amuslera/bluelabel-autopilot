"""
Prompt template loader for bluelabel-autopilot
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class PromptLoader:
    """Load and manage prompt templates from YAML files."""
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize the prompt loader.
        
        Args:
            base_path: Base directory for prompt templates. 
                      Defaults to prompts directory relative to this file.
        """
        if base_path is None:
            base_path = Path(__file__).parent
        self.base_path = Path(base_path)
    
    def load_template(self, template_path: str) -> Dict[str, Any]:
        """Load a prompt template from a YAML file.
        
        Args:
            template_path: Path to template file relative to base_path
            
        Returns:
            Dictionary containing the prompt template configuration
            
        Raises:
            FileNotFoundError: If template file doesn't exist
            yaml.YAMLError: If template file is invalid YAML
        """
        full_path = self.base_path / template_path
        if not full_path.exists():
            raise FileNotFoundError(f"Template not found: {full_path}")
            
        with open(full_path, 'r') as f:
            return yaml.safe_load(f)
    
    def render_prompt(self, template: Dict[str, Any], **kwargs) -> Dict[str, str]:
        """Render a prompt template with provided variables.
        
        Args:
            template: Loaded template dictionary
            **kwargs: Variables to substitute in the template
            
        Returns:
            Dictionary with rendered prompts (system, user, assistant)
        """
        prompt_template = template.get('prompt_template', {})
        rendered = {}
        
        for key in ['system', 'user', 'assistant']:
            if key in prompt_template:
                prompt_text = prompt_template[key]
                # Simple variable substitution
                for var_name, var_value in kwargs.items():
                    prompt_text = prompt_text.replace(f"{{{{ {var_name} }}}}", str(var_value))
                rendered[key] = prompt_text
                
        return rendered
    
    def get_config(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Extract configuration from a template.
        
        Args:
            template: Loaded template dictionary
            
        Returns:
            Configuration dictionary
        """
        return template.get('config', {})


# Example usage
if __name__ == "__main__":
    loader = PromptLoader()
    
    # Load summarization template
    template = loader.load_template("contentmind/summarization.yaml")
    config = loader.get_config(template)
    
    # Render with content
    rendered = loader.render_prompt(
        template,
        content="This is sample content to summarize..."
    )
    
    print("Model:", config.get('model'))
    print("System prompt:", rendered.get('system', '')[:100] + "...")