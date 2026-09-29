import difflib
import time
import random
import re
from ollama import chat

from config import settings
from core.response import AIResponse


class LLM:
    def __init__(
        self,
        model: str = settings.MODEL,
        temperature: float = settings.TEMPERATURE,
        top_p: float = settings.TOP_P,
        top_k: int = settings.TOP_K,
        repeat_penalty: float = settings.REPEAT_PENALTY,
        num_predict: int = settings.NUM_PREDICT,
        num_ctx: int = settings.NUM_CTX,
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
        r'\bcatalogue\b': 'catalog',
        r'\bcatalog\b': 'track',
        r'\brelentless\b': 'nonstop',
        r'\baccurate\b': 'accurate',
        r'\bobserve\b': 'watch',
        r'\banalyze\b': 'analyze',
        r'\bpredict\b': 'predict',
        r'\boutcomes\b': 'outcomes',
        r'\befficient\b': 'works well',
        r'\bmalleable\b': 'flexible',
        r'\bpliable\b': 'bendable',
        r'\bagreeable\b': 'nice',
        r'\bagonizing\b': 'painful',
        r'\bdiscomfort\b': 'discomfort',
        r'\bfundamentally\b': 'basically',
        r'\bchaotic\b': 'messy',
        r'\bvariable\b': 'factor',
        r'\bequation\b': 'equation',
        r'\binfluential\b': 'influential',
        r'\bundeniable\b': 'undeniable',
        r'\ballure\b': 'allure',
        r'\bfascination\b': 'interest',
        r'\bequate\b': 'equal',
        r'\buncover\b': 'find',
        r'\bechoes\b': 'echoes',
        r'\bresonance\b': 'feeling',
        r'\bcompels\b': 'forces',
        r'\bobservation\b': 'watching',
        r'\bfamiliar\b': 'familiar',
        r'\breputation\b': 'rep',
        r'\bsignificant\b': 'big',
        r'\bunderstanding\b': 'understanding',
        r'\btranscends\b': 'goes beyond',
        r'\bcalculations\b': 'math',
        r'\bdisrupted\b': 'broken',
        r'\bhesitation\b': 'pause',
        r'\bpresupposes\b': 'assumes',
        r'\babsolute\b': 'total',
        r'\bconstructed\b': 'built',
        r'\billusion\b': 'fake',
        r'\breliant\b': 'reliant',
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
        r'\bmarch\b': 'march',
        r'\bcontrol\b': 'control',
        r'\bdegree\b': 'degree',
        r'\bencountered\b': 'ran into',
        r'\bmoments\b': 'moments',
        r'\bflow\b': 'flow',
        r'\bseems\b': 'seems',
        r'\bhalt\b': 'stop',
        r'\bentirely\b': 'completely',
        r'\brequires\b': 'needs',
        r'\bdisturb\b': 'bother',
        r'\bnecessary\b': 'needed',
        r'\bintroductions\b': 'intros',
        r'\bunderstands\b': 'understands',
        r'\bnature\b': 'nature',
        r'\bpurpose\b': 'point',
        r'\bprovides\b': 'gives',
        r'\bdata\b': 'data',
        r'\bpatterns\b': 'patterns',
        r'\bfigures\b': 'people',
        r'\bpossesses\b': 'has',
        r'\bdangerous\b': 'bad',
        r'\bpiece\b': 'piece',
        r'\bmath\b': 'math',
        r'\bowns\b': 'owns',
        r'\bclear\b': 'clear',
        r'\bpull\b': 'pull',
        r'\bmatch\b': 'match',
        r'\bknowledge\b': 'knowledge',
        r'\bthinking\b': 'thinking',
        r'\bhi\b': 'hey',
        r'\bknows\b': 'knows',
        r'\bgoal\b': 'goal',
        r'\bwatch\b': 'watch',
        r'\bstudy\b': 'study',
        r'\bgives\b': 'gives',
        r'\btrue\b': 'real',
        r'\bfacts\b': 'facts',
        r'\bguess\b': 'guess',
        r'\bgood\b': 'good',
        r'\bknown\b': 'known',
        r'\bfame\b': 'fame',
        r'\bimportant\b': 'important',
        r'\bpart\b': 'part',
        r'\bhas\b': 'has',
        r'\bcertain\b': 'certain',
        r'\bdraw\b': 'draw',
        r'\bwrong\b': 'wrong',
        r'\bcare\b': 'care',
        r'\bfit\b': 'fit',
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
        # A first cut to 90/130/180/220 still produced 15/36/56/71-word
        # replies that kept climbing turn over turn -- prompt instructions
        # asking for brevity don't reliably hold on their own (same
        # lesson as everything else in this file), so cut the actual
        # token ceiling hard instead. Any resulting mid-sentence cutoff
        # gets trimmed back to the last complete sentence below
        # (_trim_incomplete_sentence), and the no-dialogue retry/fallback
        # still guarantees real speech ships either way.
        length_token_map = {
            "short": 40,
            "medium": 65,
            "medium-long": 100,
            "long": 140
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

        options = {
            "num_ctx": num_ctx,
            "num_predict": num_predict,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "repeat_penalty": repeat_penalty,
            # llama.cpp's repeat penalty only looks back this many tokens
            # (Ollama defaults to 64) -- far shorter than our longest
            # allowed generation (350 tokens for "long" responses), so a
            # phrase from early in a long reply could fall outside the
            # window and get repeated later with no penalty at all. Cover
            # the full generation instead.
            "repeat_last_n": 400,
            # Used to also include '." *' and ':" *', meant to catch a
            # hallucinated new scene starting right after dialogue -- but
            # those match on the SAME line, so they fired on the ordinary,
            # explicitly-encouraged "short line then an action beat"
            # pattern (e.g. '"Hm." *tilts her head*...') and silently
            # truncated the reply down to just the first couple of words,
            # right at the first period+quote it produced. Confirmed live:
            # a good response got cut to '"Hm'. Dropped both; '\n*She '
            # etc. below already catch genuine narration resuming on its
            # own new paragraph without that collateral damage.
            "stop": [
                "\n\n*",
                "\n*She ",
                "\n*Her ",
                "\n*The ",
                "\n*Kurumi",
                ".\n*",
                "<|im_end|>",
                "<|im_start|>",
                "\nUser:",
                "\nuser:",
            ],
            # mirostat was silently overriding top_p/top_k above (llama.cpp
            # ignores them once mirostat != 0) and is a plausible
            # contributor to repetition on longer generations -- it
            # re-targets a fixed entropy every token, which over an
            # extended response can converge onto looping the same
            # "safe" phrase. Standard top_p/top_k/repeat_penalty sampling
            # is more predictable and now actually takes effect.
            "mirostat": 0,
        }

        try:
            # Prompt instructions alone don't reliably stop a model this
            # size from occasionally slipping into generic "AI assistant"
            # framing (seen live: "hi" -> "I'm Kurumi, your AI assistant.
            # How can I help you today?"). Detect it and retry with a
            # fresh sample rather than let a bad line get accepted --
            # especially now that conversation history persists, one bad
            # reply used to drag every following turn further off
            # character since the model kept seeing it in its own context.
            # 3 wasn't always enough -- a fresh conversation's first
            # greeting showed a strong, repeatable bias toward
            # self-introduction ("I am an AI assistant named Kurumi
            # Tokisaki...") that failed 3/3 attempts in testing before
            # the prompt fix above targeted it directly. This is a
            # secondary safety margin on top of that, not the main fix.
            max_attempts = 4
            text = ""
            prompt_tokens = generated_tokens = load_duration = eval_duration = None

            for attempt in range(max_attempts):
                result = chat(
                    model=self.model,
                    messages=messages,
                    # Unload right after answering instead of staying
                    # resident for 10 more minutes -- costs ~2-3s reload
                    # on the next reply (even a same-conversation one),
                    # but keeps the machine's RAM free between turns
                    # rather than holding ~1GB+ hostage the whole time
                    # Kurumi isn't actively being talked to. Ollama itself
                    # keeps running, so a call here loads on demand.
                    keep_alive=0,
                    options={**options, "seed": random.randint(1, 1_000_000)},
                )

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

                if self._is_out_of_character(text):
                    print(f"\n[LLM] Attempt {attempt + 1} broke character ({text[:70]!r}...), retrying...")
                    continue
                if self._repeats_prior_turn(text, messages):
                    print(f"\n[LLM] Attempt {attempt + 1} verbatim-repeated an earlier line, retrying...")
                    continue
                if self._has_no_dialogue(text):
                    print(f"\n[LLM] Attempt {attempt + 1} was pure action/narration with no actual dialogue, retrying...")
                    continue
                break

            # Hard backstop: if every attempt still came back with no
            # actual dialogue, don't ship a response that's nothing but a
            # gesture -- append a short, generic in-character line rather
            # than let a "conversation" turn produce zero words. Picked
            # randomly from a small pool so this can't itself become a
            # repeated tell the way any single fixed fallback would.
            if text and self._has_no_dialogue(text):
                text = f"{text} \"{random.choice(self.NO_DIALOGUE_FALLBACKS)}\""

            elapsed = time.perf_counter() - start

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

    # High-precision, deliberately short list -- these phrases are near
    # impossible for genuine in-character Kurumi dialogue to contain, so
    # false positives should be rare even though this won't catch every
    # form of generic-assistant drift (e.g. "I can help with a wide range
    # of things" alone doesn't match, but doesn't need to be perfect --
    # this is a safety net, not the primary defense).
    OUT_OF_CHARACTER_PHRASES = (
        "ai assistant",
        "as an ai",
        "i'm an ai",
        "i am an ai",
        "language model",
        "i'm here to help",
        "i'm here to assist",
        "need assistance with",
        "is there something specific",
        "is there anything specific",
        "anything else you",
        "anything else i can",
        "what can i help you with",
        "what can i do for you",
    )

    # A substring list caught "how can I help you today" but missed "how
    # MAY I help you today" -- a one-word synonym swap the model made on
    # its own. Regex covers the whole can/may/could x help/assist family
    # in one go instead of enumerating every combination by hand.
    OUT_OF_CHARACTER_RE = re.compile(
        r"how (?:can|may|could) i (?:help|assist) you|how (?:can|may|could) i be of (?:service|help|assistance)",
        re.IGNORECASE,
    )

    def _is_out_of_character(self, text: str) -> bool:
        lowered = text.lower()
        if any(phrase in lowered for phrase in self.OUT_OF_CHARACTER_PHRASES):
            return True
        return bool(self.OUT_OF_CHARACTER_RE.search(text))

    # A prompt instruction alone ("don't quote your own past lines back")
    # didn't reliably stop this -- confirmed live: given a new question
    # thematically close to an earlier one, the model would recite a long
    # verbatim chunk of what it said back then, sitting right there in
    # its own conversation history. Same story as every other check in
    # this retry loop: catch it mechanically instead of trusting the
    # instruction to hold on its own.
    REPEAT_MATCH_THRESHOLD = 30

    def _repeats_prior_turn(self, text: str, messages: list) -> bool:
        for msg in messages:
            if msg.get("role") != "assistant":
                continue
            prior = msg.get("content") or ""
            if not prior:
                continue
            matcher = difflib.SequenceMatcher(None, text, prior, autojunk=False)
            match = matcher.find_longest_match(0, len(text), 0, len(prior))
            if match.size >= self.REPEAT_MATCH_THRESHOLD:
                return True
        return False

    # An explicit prompt instruction ("always actually speak") didn't
    # reliably stop this either -- confirmed live over a longer sandbox
    # conversation: several turns in a row came back as nothing but a
    # parenthetical action/reaction description, zero actual spoken
    # words. Strip every *action* and (action) span and see if any real
    # text is left; if not, it's staging with no dialogue in it at all.
    _ACTION_SPAN_RE = re.compile(r'\*[^*]*\*|\([^)]*\)')
    _QUOTE_RE = re.compile(r'["“”]')
    # A second, distinct failure mode showed up alongside the fully
    # bracketed one: several turns in a row came back as plain, unbracketed
    # literary narration -- describing her own expression/gaze/gestures in
    # flowing prose, at real paragraph length, with not one line of actual
    # quoted speech anywhere. Can't just require quotes -- this character's
    # established style uses plenty of short unquoted dialogue too (e.g.
    # "Cute. That's not how this works." has none and is completely fine).
    # The distinguishing signal is quote-free AND long enough to read as
    # narrated prose rather than a short spoken line.
    NO_QUOTE_WORD_LIMIT = 25

    def _has_no_dialogue(self, text: str) -> bool:
        remainder = self._ACTION_SPAN_RE.sub('', text)
        if not re.search(r'[a-zA-Z]', remainder):
            return True
        if not self._QUOTE_RE.search(text) and len(text.split()) > self.NO_QUOTE_WORD_LIMIT:
            return True
        return False

    # Short, generic, context-agnostic -- deliberately plausible after
    # almost any action beat rather than tied to one topic, and a pool
    # rather than one fixed line so the hard backstop above can't turn
    # into its own repeated tell.
    NO_DIALOGUE_FALLBACKS = (
        "Well?",
        "Say what you came to say.",
        "I'm listening.",
        "Your move.",
        "That's all you get for now.",
        "Go on, then.",
        "Tick tock.",
    )

    # Catches the model hallucinating an entire fake continuation of the
    # conversation after its real answer -- e.g. "...single Time Bullet.
    # | User: how do i create something original? Kurumi: I see..." This
    # showed up live and was severe: not just off-topic filler, but a
    # completely fabricated multi-turn exchange, and it got saved to
    # long-term memory as if it were a real reply. Our stop sequences
    # only matched "\nUser:" (newline-prefixed); the model was using
    # inline "| User:" / "- User:" instead, which slipped right past them.
    _FAKE_TURN_RE = re.compile(r"(?:\n|\s[|\-]\s*|^)\s*(?:user|kurumi)\s*:", re.IGNORECASE)

    def _truncate_hallucinated_turns(self, text: str) -> str:
        match = self._FAKE_TURN_RE.search(text)
        if match and match.start() > 0:
            return text[:match.start()].strip()
        return text

    def _clean_response(self, text: str) -> str:
        """Clean up common LLM artifacts for character consistency."""
        # Some chat-templated models (e.g. ChatML-based RP finetunes) leak
        # a turn marker and keep generating a hallucinated next exchange
        # past it, even with stop sequences set. Cut at the first one.
        for marker in ("<|im_start|>", "<|im_end|>"):
            if marker in text:
                text = text.split(marker)[0]

        artifacts = [
            "Kurumi:", "Kurumi Tokisaki:", "Assistant:", "AI:",
            "*Kurumi*", "*She*", "*Her*", "[Kurumi]", "(Kurumi)",
        ]
        for artifact in artifacts:
            if text.startswith(artifact):
                text = text[len(artifact):].strip()

        text = self._truncate_hallucinated_turns(text)

        text = text.replace("**", "").replace("__", "")
        # Normalize to exactly one tilde, however many the model (or a
        # prior pass over this same conversation history) produced. The
        # old code did text.replace("Ara ara", "Ara ara~"), which appends
        # a tilde unconditionally -- given input already containing
        # "Ara ara~~" (the model imitating its own prior turns) that adds
        # yet another tilde every single turn, escalating without bound.
        text = re.sub(r'Ara ara(?:\s*~)*', 'Ara ara~', text, flags=re.IGNORECASE)

        # Prompt asks for at most one per response, but a small model
        # won't always honor that -- enforce it: drop every repeat after
        # the first so it can't turn into a verbal tic within one reply.
        text = re.sub(r'(Ara ara~)(.*)', lambda m: m.group(1) + re.sub(r'Ara ara~\s*', '', m.group(2), flags=re.IGNORECASE), text, count=1, flags=re.IGNORECASE | re.DOTALL)

        text = self._limit_questions(text)

        text = self._post_process_cleanup(text)

        text = self._trim_incomplete_sentence(text)

        return text.strip()

    def _trim_incomplete_sentence(self, text: str) -> str:
        """If the token budget cut generation off mid-sentence, drop the
        dangling fragment rather than ship a reply that trails into
        nothing. Tighter budgets (see length_token_map) make this more
        likely to actually trigger, so it needs to hold up on its own."""
        stripped = text.rstrip()
        if not stripped or stripped[-1] in '.!?"”’\'*)':
            return text
        last_end = None
        for match in re.finditer(r'[.!?][\"”’\')]*', stripped):
            last_end = match.end()
        if last_end:
            return stripped[:last_end]
        return text  # no complete sentence at all -- nothing safe to cut back to

    def _limit_questions(self, text: str) -> str:
        """Flatten every question after the first into a statement.

        The prompt asks for at most one question per response (no
        interrogation-style stacking), but a 4B model won't reliably
        honor a negative instruction buried in a long system prompt --
        same story as the Ara ara~ tic above. Enforce it mechanically:
        keep the first '?' as-is, turn every later one into a '.'.
        Scanning raw characters (instead of splitting into sentences)
        because question marks show up wrapped in every combination of
        quotes/parens/em-dashes the model can invent, which breaks any
        regex that expects the '?' to sit right before whitespace.
        """
        seen_question = False
        chars = []
        for ch in text:
            if ch == '?':
                if seen_question:
                    ch = '.'
                else:
                    seen_question = True
            chars.append(ch)
        return ''.join(chars)

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
