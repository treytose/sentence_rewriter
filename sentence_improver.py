import os, random
from dotenv import load_dotenv
import keyboard
import pyperclip
import openai
import time
from rich.prompt import Prompt
from rich.console import Console
from rich.progress import Progress

# Initialize the console for rich output
console = Console()

# Load environment variables from the .env file
load_dotenv()

# Global variable to hold styles and prompts
sentence_styles = {
    "1": {"name": "Default", "prompt": "Improve this sentence, only provide the improved sentence: {sentence}"},
    "2": {"name": "Lillia", "prompt": "Rewrite this sentence in the style of a shy and bashful Lillia from league of legends. Include some stutter and shyness. Only provide the rewritten sentence: {sentence}"},
    "3": {"name": "Yummi", "prompt": "Rewrite this sentence in the style of a playful and mischievous Yummi from league of legends. Only provide the improved sentence: {sentence}"},
    "4": {"name": "Giga Chad", "prompt": "Rewrite this sentence in the style of a confident and assertive Giga Chad. Only provide the improved sentence: {sentence}"},
    "5": {"name": "Condescending", "prompt": "Rewrite this sentence the style of A condescending, obnoxious speaking style characterized by slow, exaggerated enunciation, using unnecessarily complex vocabulary and jargon to flaunt knowledge. The tone is smug and pretentious, with frequent interruptions to correct or 'educate' others, often speaking down to them as if they are intellectually inferior. The speaker uses every opportunity to steer conversations toward topics where they can showcase their supposed expertise, resulting in an overly self-important, irritating delivery. Only provide the improved sentence: {sentence}"},
    # Add more styles as needed
}

def improve_sentence(sentence, style_key):
    """Queries OpenAI's Chat API (GPT) to improve the sentence with the selected style."""
    try:
        client = openai.OpenAI()

        # Get the style prompt based on the selected key
        prompt_template = sentence_styles.get(style_key, sentence_styles["1"])["prompt"]
        prompt = prompt_template.format(sentence=sentence)

        # Show a loading spinner while querying the AI
        with Progress(console=console) as progress:
            task = progress.add_task("[green]Querying OpenAI...", total=None)
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Adjust the model as needed, "gpt-4" for GPT-4 model
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            progress.remove_task(task)

        improved_sentence = response.choices[0].message.content
        return improved_sentence
    except Exception as e:
        console.print(f"[red]Error querying OpenAI API:[/red] {e}")
        return sentence

# Display the dynamic menu with available styles
console.print("[bold green]Choose style:[/bold green]")
for key, style in sentence_styles.items():
    console.print(f"{key}. {style['name']}")

# Ask the user to enter a number corresponding to their choice
style_choice = input(f"Enter the number for the style you want ({'/'.join(sentence_styles.keys())}): ")

# Validate the input and set the style accordingly, defaulting to "1" if invalid
style_key = style_choice if style_choice in sentence_styles else "1"
if style_choice not in sentence_styles:
    console.print("[yellow]Invalid choice. Using default style.[/yellow]")

# Ask the user whether to paste the improved sentence or type it out key by key
typing_method_choice = Prompt.ask("Choose sentence output method", choices=["paste", "type"], default="paste")

def on_hotkey():
    """Triggered when the hotkey is pressed."""
    
    # Wait for clipboard data to populate
    time.sleep(0.2)
    
    # Get the copied text
    sentence = pyperclip.paste()
    sentence = sentence.strip()

    # max length of the sentence is 150 characters
    if len(sentence) > 150:
        console.print("[yellow]The sentence is too long. Please select a shorter sentence.[/yellow]")
        return
    
    if sentence:
        console.print(f"Sentence to improve: [blue]{sentence}[/blue]")
        # Call the OpenAI API to improve the sentence with the chosen style
        improved_sentence = improve_sentence(sentence, style_key)
        
        # Replace the clipboard content with the improved sentence
        pyperclip.copy(improved_sentence)
        
        if typing_method_choice == "paste":
            # Simulate pressing CTRL+V to paste the improved sentence
            keyboard.send("ctrl+v")
        else:
            # Simulate typing the sentence key by key
            for char in improved_sentence:
                # Simulate random backspace corrections with a small chance
                if random.random() < 0.02:  # 2% chance of making a mistake
                    keyboard.write(random.choice(improved_sentence))  # "Mistake" character
                    time.sleep(random.uniform(0.05, 0.15))  # Slight delay before correcting
                    keyboard.send("backspace")
                
                # Write the correct character
                keyboard.write(char)

                # Simulate human typing variability with random delays
                time.sleep(random.uniform(0.01, 0.05))  # Faster on some chars, slower on others
                
                # Simulate longer pauses after spaces or punctuation
                if char in ".,!? ":
                    time.sleep(random.uniform(0.05, 0.2))  # Short pause after punctuation or space
        
        console.print(f"[green]Improved sentence:[/green] {improved_sentence}")
    else:
        console.print("[yellow]No text highlighted or copied.[/yellow]")

# Set the hotkey to Ctrl+c to trigger the improvement function
keyboard.add_hotkey("ctrl+c", on_hotkey)

console.print("[green]Script running. Press ctrl+c to improve highlighted sentence.[/green]")

# Keep the script running
keyboard.wait("esc")  # Exit the script by pressing 'esc'
