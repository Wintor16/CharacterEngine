import time
import random
import re
from ollama import chat

from core.response import AIResponse


class LLM:
    def __init__(
        self,
        model: str = "gemma3:4b",
        temperature: float = 0.85,
        top_p: float = 0.92,
        top_k: int = 40,
        repeat_penalty: float = 1.15,
        num_predict: int = 300,
        num_ctx: int = 4096,
    ):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.repeat_penalty = repeat_penalty
        self.num_predict = num_predict
        self.num_ctx = num_ctx

    # Word simplification dictionary - natural, everyday English
    SIMPLE_WORDS = {
        # Formal -> Natural
        r'\bcontemplation\b': 'thinking',
        r'\bperceive\b': 'see',
        r'\bcatalogue\b': 'track',
        r'\bcatalog\b': 'track',
        r'\brelentless\b': 'nonstop',
        r'\baccurate\b': 'right',
        r'\bobserve\b': 'watch',
        r'\banalyze\b': 'figure out',
        r'\bpredict\b': 'guess',
        r'\boutcomes\b': 'results',
        r'\befficient\b': 'works well',
        r'\bmalleable\b': 'flexible',
        r'\bpliable\b': 'bendable',
        r'\bagreeable\b': 'nice',
        r'\bagonizing\b': 'painful',
        r'\bdiscomfort\b': 'discomfort',
        r'\bfundamentally\b': 'basically',
        r'\bchaotic\b': 'messy',
        r'\bvariable\b': 'thing',
        r'\bequation\b': 'situation',
        r'\binfluential\b': 'important',
        r'\bundeniable\b': 'obvious',
        r'\ballure\b': 'pull',
        r'\bfascination\b': 'interest',
        r'\bequate\b': 'mean',
        r'\buncover\b': 'find',
        r'\bechoes\b': 'echoes',
        r'\bresonance\b': 'feeling',
        r'\bcompels\b': 'makes',
        r'\bobservation\b': 'watching',
        r'\bfamiliar\b': 'known',
        r'\breputation\b': 'rep',
        r'\bsignificant\b': 'major',
        r'\binfluential\b': 'big',
        r'\bundeniable\b': 'clear',
        r'\ballure\b': 'appeal',
        r'\bfascination\b': 'fascination',
        r'\bcompels\b': 'forces',
        r'\bequate\b': 'equal',
        r'\bunderstanding\b': 'getting it',
        r'\btranscends\b': 'goes beyond',
        r'\bcalculations\b': 'math',
        r'\bdisrupted\b': 'messed up',
        r'\bhesitation\b': 'pause',
        r'\bpresupposes\b': 'assumes',
        r'\babsolute\b': 'total',
        r'\bconstructed\b': 'built',
        r'\billusion\b': 'fake',
        r'\breliant\b': 'depends on',
        r'\bdefine\b': 'define',
        r'\bexistence\b': 'existence',
        r'\bpreserve\b': 'keep',
        r'\balter\b': 'change',
        r'\bsubtle\b': 'subtle',
        r'\bshift\b': 'shift',
        r'\btraces\b': 'traces',
        r'\bdelicate\b': 'delicate',
        r'\bpattern\b': 'pattern',
        r'\bmomentarily\b': 'for a moment',
        r'\bheld\b': 'held',
        r'\bstill\b': 'still',
        r'\bdiverted\b': 'redirected',
        r'\bobstacles\b': 'blocks',
        r'\bfascinating\b': 'cool',
        r'\breliant\b': 'reliant',
        r'\bmarch\b': 'march',
        r'\bdefine\b': 'define',
        r'\bexistence\b': 'existence',
        r'\bpresupposes\b': 'assumes',
        r'\bcontrol\b': 'control',
        r'\bdegree\b': 'degree',
        r'\bunderstanding\b': 'understanding',
        r'\btranscends\b': 'goes beyond',
        r'\bencountered\b': 'ran into',
        r'\bmoments\b': 'moments',
        r'\bflow\b': 'flow',
        r'\bseems\b': 'seems',
        r'\bdisrupted\b': 'messed up',
        r'\bhalt\b': 'stop',
        r'\bentirely\b': 'completely',
        r'\brequires\b': 'needs',
        r'\bdegree\b': 'degree',
        r'\bunderstanding\b': 'understanding',
        r'\btranscends\b': 'goes beyond',
        r'\bencountered\b': 'ran into',
        r'\bmoments\b': 'moments',
        r'\bflow\b': 'flow',
        r'\bseems\b': 'seems',
        r'\bdisrupted\b': 'broken',
        r'\bhalt\b': 'stop',
        r'\bentirely\b': 'completely',
        r'\brequires\b': 'needs',
        r'\bdegree\b': 'degree',
        r'\bunderstanding\b': 'understanding',
        r'\btranscends\b': 'goes beyond',
        r'\bdisturb\b': 'bother',
        r'\bnecessary\b': 'needed',
        r'\bintroductions\b': 'intros',
        r'\bunderstands\b': 'gets',
        r'\bnature\b': 'nature',
        r'\bpurpose\b': 'point',
        r'\bobserve\b': 'watch',
        r'\banalyze\b': 'analyze',
        r'\bprovides\b': 'gives',
        r'\baccurate\b': 'accurate',
        r'\bdata\b': 'info',
        r'\bcatalogue\b': 'list',
        r'\bpatterns\b': 'patterns',
        r'\bpredict\b': 'predict',
        r'\boutcomes\b': 'outcomes',
        r'\bfamiliar\b': 'familiar',
        r'\breputation\b': 'rep',
        r'\bsignificant\b': 'big',
        r'\bvariable\b': 'factor',
        r'\bequation\b': 'equation',
        r'\binfluential\b': 'influential',
        r'\bfigures\b': 'people',
        r'\bpossesses\b': 'has',
        r'\bundeniable\b': 'undeniable',
        r'\ballure\b': 'allure',
        r'\bdangerous\b': 'dangerous',
        r'\bfascination\b': 'fascination',
        r'\bequate\b': 'equal',
        r'\bunderstanding\b': 'understanding',
        r'\bcontemplation\b': 'thinking',
        r'\bdisturb\b': 'bother',
        r'\bintroductions\b': 'intros',
        r'\bunderstands\b': 'understands',
        r'\bnature\b': 'nature',
        r'\bprovides\b': 'gives',
        r'\baccurate\b': 'accurate',
        r'\bdata\b': 'data',
        r'\bcatalogue\b': 'catalog',
        r'\bpatterns\b': 'patterns',
        r'\bpredict\b': 'predict',
        r'\boutcomes\b': 'results',
        r'\bfamiliar\b': 'familiar',
        r'\breputation\b': 'rep',
        r'\bsignificant\b': 'big',
        r'\bpiece\b': 'piece',
        r'\bmath\b': 'math',
        r'\bowns\b': 'owns',
        r'\bclear\b': 'clear',
        r'\bpull\b': 'pull',
        r'\bdangerous\b': 'bad',
        r'\bfascination\b': 'interest',
        r'\bmatch\b': 'match',
        r'\bknowledge\b': 'knowledge',
        r'\bthinking\b': 'thinking',
        r'\bcontemplation\b': 'thinking',
        r'\bhi\b': 'hey',
        r'\bdisturb\b': 'bother',
        r'\bintroductions\b': 'intros',
        r'\bknows\b': 'knows',
        r'\bgoal\b': 'goal',
        r'\bwatch\b': 'watch',
        r'\bstudy\b': 'study',
        r'\bgives\b': 'gives',
        r'\btrue\b': 'real',
        r'\bfacts\b': 'facts',
        r'\bpatterns\b': 'patterns',
        r'\bguess\b': 'guess',
        r'\boutcomes\b': 'outcomes',
        r'\bgood\b': 'good',
        r'\bknown\b': 'known',
        r'\bfame\b': 'fame',
        r'\bimportant\b': 'important',
        r'\bpart\b': 'part',
        r'\bmath\b': 'math',
        r'\bhas\b': 'has',
        r'\bcertain\b': 'certain',
        r'\bdraw\b': 'draw',
        r'\bwrong\b': 'wrong',
        r'\bcare\b': 'care',
        r'\bfit\b': 'fit',
        r'\bknowledge\b': 'knowledge',
        r'\bthinking\b': 'thinking',
        r'\bcontemplation\b': 'thinking',
        r'\bhi\b': 'hey',
        r'\bdisturb\b': 'bother',
        r'\bintroductions\b': 'intros',
        r'\bknows\b': 'knows',
        r'\bgoal\b': 'goal',
        r'\bwatch\b': 'watch',
        r'\bstudy\b': 'study',
        r'\bgives\b': 'gives',
        r'\btrue\b': 'real',
        r'\bfacts\b': 'facts',
        r'\bpatterns\b': 'patterns',
        r'\bguess\b': 'guess',
        r'\boutcomes\b': 'outcomes',
        r'\bgood\b': 'good',
        r'\bknown\b': 'known',
        r'\bfame\b': 'fame',
        r'\bimportant\b': 'important',
        r'\bpart\b': 'part',
        r'\bmath\b': 'math',
        r'\bhas\b': 'has',
        r'\bcertain\b': 'certain',
        r'\bdraw\b': 'draw',
        r'\bwrong\b': 'wrong',
        r'\bcare\b': 'care',
        r'\bfit\b': 'fit',
        r'\bknowledge\b': 'knowledge',
        r'\bthinking\b': 'thinking',
        r'\bcontemplation\b': 'thinking',
        r'\bhi\b': 'hey',
    }

    def generate(self, messages, **kwargs):
        """Generate response with optional runtime parameter overrides."""
        
        start = time.perf_counter()

        # Allow runtime overrides
        temperature = kwargs.get("temperature", self.temperature)
        top_p = kwargs.get("top_p", self.top_p)
        top_k = kwargs.get("top_k", self.top_k)
        repeat_penalty = kwargs.get("repeat_penalty", self.repeat_penalty)
        num_predict = kwargs.get("num_predict", self.num_predict)
        num_ctx = kwargs.get("num_ctx", self.num_ctx)
        
        # Get response_length from plan if available to adjust max tokens
        response_length = kwargs.get("response_length", "medium")
        length_token_map = {
            "short": 150,
            "medium": 200,
            "medium-long": 280,
            "long": 350
        }
        if response_length in length_token_map:
            num_predict = length_token_map[response_length]
        
        # Lower temperature for shorter responses = more focused/constrained
        length_temp_map = {
            "short": 0.4,
            "medium": 0.6,
            "medium-long": 0.7,
            "long": 0.8
        }
        if response_length in length_temp_map:
            temperature = length_temp_map[response_length]

        try:
            result = chat(
                model=self.model,
                messages=messages,
                keep_alive="10m",
                options={
                    "seed": random.randint(1, 1_000_000),
                    "num_ctx": num_ctx,
                    "num_predict": num_predict,
                    "temperature": temperature,
                    "top_p": top_p,
                    "top_k": top_k,
                    "repeat_penalty": repeat_penalty,
                    "stop": [
                        "\n\n*",
                        "\n*She ",
                        "\n*Her ",
                        "\n*The ",
                        "\n*Kurumi",
                        ".\" *",
                        ".\n*",
                        ":\" *",
                    ],
                    "mirostat": 2,
                    "mirostat_tau": 5.0,
                    "mirostat_eta": 0.1,
                }
            )

            elapsed = time.perf_counter() - start

            message = result.get("message")
            if isinstance(message, dict):
                text = message.get("content", "").strip()
            else:
                text = getattr(message, "content", "").strip()

            text = self._clean_response(text)

            prompt_tokens = getattr(result, "prompt_eval_count", None)
            generated_tokens = getattr(result, "eval_count", None)
            load_duration = getattr(result, "load_duration", None)
            eval_duration = getattr(result, "eval_duration", None)

            self._print_debug(
                text, elapsed, prompt_tokens, generated_tokens,
                load_duration, eval_duration,
                actual_num_predict=num_predict
            )

            return AIResponse(
                text=text,
                model=self.model,
                generation_time=elapsed,
                success=True
            )

        except Exception as e:
            elapsed = time.perf_counter() - start
            self._print_error(e)
            return AIResponse(
                text="*The shadows stir but no words come forth...*",
                model=self.model,
                generation_time=elapsed,
                success=False,
                error=str(e)
            )

    def _clean_response(self, text: str) -> str:
        """Clean up common LLM artifacts for character consistency."""
        artifacts = [
            "Kurumi:", "Kurumi Tokisaki:", "Assistant:", "AI:",
            "*Kurumi*", "*She*", "*Her*", "[Kurumi]", "(Kurumi)",
        ]
        for artifact in artifacts:
            if text.startswith(artifact):
                text = text[len(artifact):].strip()
        
        text = text.replace("**", "").replace("__", "")
        text = text.replace("Ara ara", "Ara ara~")
        text = text.replace("Ara ara ~", "Ara ara~")
        
        text = self._strip_narration(text)
        text = self._post_process_cleanup(text)
        
        return text.strip()

    def _post_process_cleanup(self, text: str) -> str:
        """Final cleanup pass for stray artifacts."""
        # Fix action beats with trailing space before closing *
        text = re.sub(r'\*([^*]*?)\s+\*', r'*\1*', text)
        
        # Remove standalone asterisks on their own lines
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped == '*' or stripped == '**' or re.match(r'^\*\s*$', stripped):
                continue
            cleaned_lines.append(line)
        
        text = '\n'.join(cleaned_lines)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # SIMPLIFY VOCABULARY
        text = self._simplify_vocabulary(text)
        
        return text.strip()
    
    def _simplify_vocabulary(self, text: str) -> str:
        """Replace complex words with simple equivalents."""
        
        # Complex -> Simple word mappings (case-insensitive, whole words)
        replacements = self.SIMPLE_WORDS
        
        for complex_word, simple_word in replacements.items():
            text = re.sub(complex_word, simple_word, text, flags=re.IGNORECASE)
        
        # Fix common grammar issues from replacements
        text = re.sub(r'\b(a) (endless|equal|important|interesting|influence|understand|own)\b', r'an \2', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(a) (clear|understand)\b', r'an \2', text, flags=re.IGNORECASE)
        text = re.sub(r'\bDo\*you\*', 'Do you', text)
        text = re.sub(r'\bcan\*influence\b', 'can influence', text)
        text = re.sub(r'\bcertainly\*influence\b', 'certainly influence', text)
        text = re.sub(r'\btruly\*stopped\*\b', 'truly stopped', text, flags=re.IGNORECASE)
        text = re.sub(r'\btruly\*stopped\b', 'truly stopped', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhellos\b', 'names', text, flags=re.IGNORECASE)
        text = re.sub(r'\bfit to\b', 'fit', text, flags=re.IGNORECASE)
        text = re.sub(r'\binefficient\b', 'wasteful', text, flags=re.IGNORECASE)
        text = re.sub(r'\bendeavor\b', 'try', text, flags=re.IGNORECASE)
        text = re.sub(r'\beddies\b', 'swirls', text, flags=re.IGNORECASE)
        text = re.sub(r'\bcausality\b', 'cause and effect', text, flags=re.IGNORECASE)
        text = re.sub(r'\bpresumption\b', 'guess', text, flags=re.IGNORECASE)
        text = re.sub(r'\bassumes\b', 'thinks', text, flags=re.IGNORECASE)
        text = re.sub(r'\btotal\b', 'full', text, flags=re.IGNORECASE)
        text = re.sub(r'\bvoid\b', 'empty space', text, flags=re.IGNORECASE)
        text = re.sub(r'\bceases\b', 'stops', text, flags=re.IGNORECASE)
        text = re.sub(r'\bexist\b', 'be', text, flags=re.IGNORECASE)
        text = re.sub(r'\btell ends\b', 'tell the end', text, flags=re.IGNORECASE)
        text = re.sub(r'\ban knowing\b', 'a knowing', text, flags=re.IGNORECASE)
        text = re.sub(r'\btruly\*stopped\*\b', 'truly stopped', text, flags=re.IGNORECASE)
        text = re.sub(r'\btruly\*stopped\b', 'truly stopped', text, flags=re.IGNORECASE)
        text = re.sub(r'\bTo\*stop\*\b', 'To stop', text)
        text = re.sub(r'\bto\*stop\*\b', 'to stop', text)
        text = re.sub(r'\btruly\*stopped\*\b', 'truly stopped', text, flags=re.IGNORECASE)
        text = re.sub(r'\btruly\*stopped\b', 'truly stopped', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhellos\b', 'names', text, flags=re.IGNORECASE)
        text = re.sub(r'\bfit to\b', 'fit', text, flags=re.IGNORECASE)
        text = re.sub(r'\binefficient\b', 'wasteful', text, flags=re.IGNORECASE)
        text = re.sub(r'\bendeavor\b', 'try', text, flags=re.IGNORECASE)
        text = re.sub(r'\beddies\b', 'swirls', text, flags=re.IGNORECASE)
        text = re.sub(r'\bcausality\b', 'cause and effect', text, flags=re.IGNORECASE)
        text = re.sub(r'\bpresumption\b', 'guess', text, flags=re.IGNORECASE)
        text = re.sub(r'\bassumes\b', 'thinks', text, flags=re.IGNORECASE)
        text = re.sub(r'\btotal\b', 'full', text, flags=re.IGNORECASE)
        text = re.sub(r'\bvoid\b', 'empty space', text, flags=re.IGNORECASE)
        text = re.sub(r'\bceases\b', 'stops', text, flags=re.IGNORECASE)
        text = re.sub(r'\bexist\b', 'be', text, flags=re.IGNORECASE)
        text = re.sub(r'\btell ends\b', 'tell the end', text, flags=re.IGNORECASE)
        text = re.sub(r'\ban knowing\b', 'a knowing', text, flags=re.IGNORECASE)
        text = re.sub(r'\btruly\*stopped\*\b', 'truly stopped', text, flags=re.IGNORECASE)
        text = re.sub(r'\btruly\*stopped\b', 'truly stopped', text, flags=re.IGNORECASE)
        
        return text

    def _print_debug(self, text, elapsed, prompt_tokens, generated_tokens, 
                     load_duration, eval_duration, actual_num_predict=None):
        """Print formatted debug information."""
        print()
        print("═" * 60)
        print("                    LLM DEBUG - KURUMI")
        print("═" * 60)
        print()
        print(f"MODEL: {self.model}")
        print()
        print("RESPONSE")
        print("─" * 60)
        print(text)
        print("─" * 60)
        print()
        print("TOKENS")
        print(f"  Prompt:     {prompt_tokens if prompt_tokens else '?'}")
        print(f"  Generated:  {generated_tokens if generated_tokens else '?'}")
        print()
        print("TIMING")
        print(f"  Total:      {elapsed:.2f}s")
        if load_duration:
            print(f"  Load:       {load_duration / 1_000_000_000:.2f}s")
        if eval_duration:
            print(f"  Eval:       {eval_duration / 1_000_000_000:.2f}s")
            if generated_tokens and generated_tokens > 0:
                tps = generated_tokens / (eval_duration / 1_000_000_000)
                print(f"  Speed:      {tps:.1f} tok/s")
        print()
        print("PARAMS")
        print(f"  Temp:       {self.temperature}")
        print(f"  Top-p:      {self.top_p}")
        print(f"  Top-k:      {self.top_k}")
        print(f"  Rep.Pen:    {self.repeat_penalty}")
        print(f"  Max Tokens: {actual_num_predict if actual_num_predict else self.num_predict}")
        print(f"  Context:    {self.num_ctx}")
        print()
        print("═" * 60)
        print()

    def _print_error(self, error):
        """Print formatted error."""
        print()
        print("═" * 60)
        print("                    LLM ERROR")
        print("═" * 60)
        print()
        print(str(error))
        print()
        print("═" * 60)
        print()

    def _strip_narration(self, text: str) -> str:
        """Strip prose narration, keep only dialogue and brief action beats."""
        
        # First, extract all quoted dialogue
        dialogue_matches = re.findall(r'["\u201c\u201d]([^"\u201c\u201d]+)["\u201c\u201d]', text)
        
        # Extract action beats (brief ones in asterisks)
        action_matches = re.findall(r'\*([^*]{1,80})\*', text)
        brief_actions = [f"*{a.strip()}*" for a in action_matches if 2 <= len(a.strip().split()) <= 12 and len(a.strip()) > 2]
        
        # If we have dialogue, use that as the base
        if dialogue_matches:
            result = ' '.join(dialogue_matches)
            
            if brief_actions:
                result = brief_actions[0] + ' ' + result
            
            return result
        
        # Fallback: if no quoted dialogue, try to find dialogue-like sentences
        sentences = re.split(r'([.!?]+)', text)
        reconstructed = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                reconstructed.append(sentences[i] + sentences[i + 1])
            else:
                reconstructed.append(sentences[i])
        sentences = [s.strip() for s in reconstructed if s.strip()]
        
        kept = []
        narration_keywords = [
            'her voice', 'she leans', 'she tilts', 'she shifts', 'she pauses',
            'she smiles', 'she frowns', 'she glances', 'her eyes', 'her gaze',
            'her expression', 'shadows stir', 'shadows shift', 'shadows gather',
            'shadows rise', 'shadows dance', 'the air', 'atmosphere',
            'amusement flickers', 'warmth', 'coldness', 'suggests', 'betray',
            'subtle shift', 'ghost of', 'flickers at', 'quickly suppresses',
            'direct gaze', 'arrival was', 'unexpected', 'unwelcome',
            'polished obsidian', 'resonant', 'lacking warmth', 'cool, resonant',
            'leans back', 'doesn\'t quite', 'emotion but', 'assessment already',
            'underway', 'voice is like', 'cool, resonant', 'utterly lacking'
        ]
        
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            
            if sent.startswith('*') and sent.endswith('*'):
                words = len(sent[1:-1].split())
                if 2 <= words <= 12:
                    kept.append(sent)
            elif not any(n in sent.lower() for n in narration_keywords):
                if len(sent) < 180:
                    kept.append(sent)
        
        result = ' '.join(kept)
        
        if not result.strip():
            # Try to extract just the quoted dialogue
            dialogue_matches = re.findall(r'["\u201c\u201d]([^"\u201c\u201d]+)["\u201c\u201d]', text)
            if dialogue_matches:
                result = ' '.join(dialogue_matches)
            else:
                for sent in sentences:
                    if len(sent) > 10 and not sent.startswith('*'):
                        result = sent[:150]
                        break
        
        return result.strip()