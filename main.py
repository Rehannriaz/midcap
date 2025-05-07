import streamlit as st
import pandas as pd
import io
import os
import json
import base64
import uuid
from datetime import datetime
import docx
import PyPDF2
import time
import re
from typing import Dict, List, Tuple, Any, Optional

# Mock imports for APIs that will be implemented in production
# Replace these with actual API implementations
class OpenAIClient:
    def analyze_script(self, script_text):
        """Mock function for script analysis with OpenAI"""
        # In production, this would call OpenAI API
        time.sleep(1)  # Simulate API call
        
        # Mock script analysis response
        characters = ["JOHN", "SARAH", "DETECTIVE MILLER", "BARTENDER"]
        scenes = [
            {"id": 1, "name": "INT. BAR - NIGHT", "characters": ["JOHN", "SARAH", "BARTENDER"], 
             "tone": "tense", "props": ["whiskey glass", "cellphone", "cigarette"]},
            {"id": 2, "name": "EXT. ALLEY - NIGHT", "characters": ["JOHN", "DETECTIVE MILLER"], 
             "tone": "suspenseful", "props": ["gun", "flashlight"]},
        ]
        character_details = {
            "JOHN": {"description": "Protagonist, mid-30s, troubled past", "emotion_baseline": "anxious"},
            "SARAH": {"description": "Love interest, smart and independent", "emotion_baseline": "confident"},
            "DETECTIVE MILLER": {"description": "Grizzled cop, seen too much", "emotion_baseline": "stern"},
            "BARTENDER": {"description": "Background character", "emotion_baseline": "neutral"}
        }
        
        return {
            "characters": characters,
            "scenes": scenes,
            "character_details": character_details,
            "relationships": [
                {"characters": ["JOHN", "SARAH"], "relationship": "romantic tension"},
                {"characters": ["JOHN", "DETECTIVE MILLER"], "relationship": "uneasy alliance"}
            ],
            "tone_analysis": "The script has a dark, noir feel with elements of psychological thriller"
        }

    def extract_dialogue(self, script_text):
        """Mock function to extract dialogue from script"""
        # In production, this would use a more sophisticated parser with OpenAI
        
        # For demo, we'll use a simple regex pattern to find character dialogue
        dialogue_pattern = r'([A-Z][A-Z\s]+)(?:\(.*?\))?\n([\s\S]+?)(?=\n\n|\n[A-Z][A-Z\s]+|\Z)'
        
        dialogues = []
        for match in re.finditer(dialogue_pattern, script_text):
            character = match.group(1).strip()
            lines = match.group(2).strip()
            dialogues.append({
                "character": character,
                "text": lines,
                "scene_id": 1,  # Would be determined by actual parsing
                "emotion": "neutral"  # Would be determined by analysis
            })
            
        return dialogues


class HumeAIClient:
    def generate_speech(self, text, character, emotion="neutral"):
        """Mock function for generating speech with HumeAI"""
        # In production, this would call HumeAI API
        time.sleep(0.5)  # Simulate API call
        
        # In a real implementation, this would return the audio file path
        audio_file = f"audio_{uuid.uuid4().hex[:8]}.mp3"
        
        # For demo purposes, return a mock audio path
        return f"https://example.com/audio/{audio_file}"
    
    def get_available_voices(self):
        """Get available voice options"""
        return [
            {"id": "voice1", "name": "Male Deep", "gender": "male", "age": "adult"},
            {"id": "voice2", "name": "Female Warm", "gender": "female", "age": "adult"},
            {"id": "voice3", "name": "Male Raspy", "gender": "male", "age": "older"},
            {"id": "voice4", "name": "Female Young", "gender": "female", "age": "young"},
            {"id": "voice5", "name": "Neutral", "gender": "neutral", "age": "adult"}
        ]


# Initialize API clients
openai_client = OpenAIClient()
hume_client = HumeAIClient()

# Set page configuration
st.set_page_config(
    page_title="AI Script Reader Platform",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state initialization
if 'current_script' not in st.session_state:
    st.session_state.current_script = None
if 'script_analysis' not in st.session_state:
    st.session_state.script_analysis = None
if 'dialogues' not in st.session_state:
    st.session_state.dialogues = []
if 'audio_clips' not in st.session_state:
    st.session_state.audio_clips = {}
if 'character_voices' not in st.session_state:
    st.session_state.character_voices = {}
if 'projects' not in st.session_state:
    st.session_state.projects = []


def extract_text_from_docx(file):
    """Extract text content from a .docx file"""
    doc = docx.Document(file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)


def extract_text_from_pdf(file):
    """Extract text content from a .pdf file"""
    pdf_reader = PyPDF2.PdfReader(file)
    text = ''
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def process_uploaded_script(uploaded_file):
    """Process an uploaded script file"""
    if uploaded_file is None:
        return None
    
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension == 'txt':
        script_content = uploaded_file.getvalue().decode('utf-8')
    elif file_extension == 'docx':
        script_content = extract_text_from_docx(uploaded_file)
    elif file_extension == 'pdf':
        script_content = extract_text_from_pdf(uploaded_file)
    else:
        st.error(f"Unsupported file format: {file_extension}")
        return None
    
    return script_content


def analyze_script(script_content):
    """Analyze script content using OpenAI"""
    with st.spinner('Analyzing script...'):
        analysis = openai_client.analyze_script(script_content)
        dialogues = openai_client.extract_dialogue(script_content)
        
        return analysis, dialogues


def generate_audio_for_line(character, text, emotion="neutral"):
    """Generate audio for a single line of dialogue"""
    voice_id = st.session_state.character_voices.get(character, "voice1")
    
    with st.spinner(f'Generating audio for {character}...'):
        audio_url = hume_client.generate_speech(text, character, emotion)
        
    return audio_url


def display_audio_player(url, character, text):
    """Display an audio player for a generated line"""
    st.audio(url, format='audio/mp3')
    st.caption(f"**{character}**: {text}")


def save_project(project_name):
    """Save current project data"""
    project = {
        "name": project_name,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "script_name": st.session_state.current_script.name if st.session_state.current_script else "Untitled",
        "analysis": st.session_state.script_analysis,
        "dialogues": st.session_state.dialogues,
        "audio_clips": st.session_state.audio_clips,
        "character_voices": st.session_state.character_voices
    }
    
    st.session_state.projects.append(project)
    st.success(f"Project '{project_name}' saved!")


# UI Components
def sidebar_menu():
    """Render the sidebar menu"""
    st.sidebar.title("AI Script Reader")
    
    menu = st.sidebar.radio("Navigation", 
                          ["Upload Script", "Script Analysis", "Audio Generation", 
                           "Scene Playback", "Project Management"])
    
    st.sidebar.markdown("---")
    
    # Display current script info if available
    if st.session_state.current_script:
        st.sidebar.subheader("Current Script")
        st.sidebar.info(f"📄 {st.session_state.current_script.name}")
        
        if st.session_state.script_analysis:
            characters = st.session_state.script_analysis.get("characters", [])
            scenes = st.session_state.script_analysis.get("scenes", [])
            st.sidebar.text(f"Characters: {len(characters)}")
            st.sidebar.text(f"Scenes: {len(scenes)}")
            st.sidebar.text(f"Dialogues: {len(st.session_state.dialogues)}")
    
    st.sidebar.markdown("---")
    st.sidebar.caption("AI Script Reader Platform v0.1")
    
    return menu


def upload_script_page():
    """Page for uploading and processing scripts"""
    st.header("Upload Script")
    
    uploaded_file = st.file_uploader("Choose a script file", 
                                     type=['txt', 'docx', 'pdf'],
                                     help="Upload a script file in TXT, DOCX, or PDF format")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Process Script", disabled=uploaded_file is None):
            script_content = process_uploaded_script(uploaded_file)
            
            if script_content:
                st.session_state.current_script = uploaded_file
                analysis, dialogues = analyze_script(script_content)
                st.session_state.script_analysis = analysis
                st.session_state.dialogues = dialogues
                st.session_state.audio_clips = {}
                
                # Initialize character voices with default values
                for character in analysis.get("characters", []):
                    if character not in st.session_state.character_voices:
                        st.session_state.character_voices[character] = "voice1"
                
                st.success(f"Script '{uploaded_file.name}' processed successfully!")
                st.rerun()
    
    with col2:
        if st.button("Clear Data", disabled=st.session_state.current_script is None):
            st.session_state.current_script = None
            st.session_state.script_analysis = None
            st.session_state.dialogues = []
            st.session_state.audio_clips = {}
            st.success("Data cleared successfully!")
            st.rerun()
    
    # Example script templates
    st.subheader("Or use a template")
    template_col1, template_col2, template_col3 = st.columns(3)
    
    with template_col1:
        if st.button("Action Scene Template"):
            # Load template script content
            template_content = """
            EXT. CITY ROOFTOP - NIGHT

            HERO
            We don't have much time. The bomb is counting down.

            SIDEKICK
            (panicking)
            What do we do now? We're trapped!

            HERO
            Trust me. I've been in worse situations.

            VILLAIN
            (from shadows)
            Have you now? I've planned for every contingency.

            Hero spins around, drawing his weapon.
            """
            
            # Create a mock uploaded file
            uploaded_file = type('obj', (object,), {
                'name': 'action_template.txt',
                'getvalue': lambda: template_content.encode('utf-8')
            })
            
            st.session_state.current_script = uploaded_file
            analysis, dialogues = analyze_script(template_content)
            st.session_state.script_analysis = analysis
            st.session_state.dialogues = dialogues
            st.session_state.audio_clips = {}
            
            # Initialize character voices
            for character in analysis.get("characters", []):
                if character not in st.session_state.character_voices:
                    st.session_state.character_voices[character] = "voice1"
                    
            st.success("Action script template loaded!")
            st.rerun()
    
    with template_col2:
        if st.button("Drama Scene Template"):
            # Load drama template (simplified for demo)
            pass
    
    with template_col3:
        if st.button("Comedy Scene Template"):
            # Load comedy template (simplified for demo)
            pass


def script_analysis_page():
    """Page for displaying script analysis results"""
    st.header("Script Analysis")
    
    if st.session_state.script_analysis is None:
        st.warning("Please upload and process a script first.")
        return
    
    analysis = st.session_state.script_analysis
    
    # Script overview
    st.subheader("Script Overview")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Total Characters:** {len(analysis.get('characters', []))}")
        st.markdown(f"**Total Scenes:** {len(analysis.get('scenes', []))}")
        st.markdown(f"**Total Dialogues:** {len(st.session_state.dialogues)}")
    
    with col2:
        st.markdown("**Tone Analysis:**")
        st.write(analysis.get("tone_analysis", "No tone analysis available"))
    
    # Character analysis
    st.subheader("Characters")
    character_tabs = st.tabs(analysis.get("characters", ["No characters"]))
    
    for i, tab in enumerate(character_tabs):
        if i < len(analysis.get("characters", [])):
            character = analysis.get("characters")[i]
            with tab:
                character_details = analysis.get("character_details", {}).get(character, {})
                st.markdown(f"**Description:** {character_details.get('description', 'No description available')}")
                st.markdown(f"**Emotional Baseline:** {character_details.get('emotion_baseline', 'Neutral')}")
                
                # Voice selection
                available_voices = hume_client.get_available_voices()
                voice_options = {v["id"]: v["name"] for v in available_voices}
                
                selected_voice = st.selectbox(
                    "Assign Voice",
                    options=list(voice_options.keys()),
                    format_func=lambda x: voice_options[x],
                    key=f"voice_select_{character}",
                    index=list(voice_options.keys()).index(st.session_state.character_voices.get(character, "voice1"))
                )
                
                st.session_state.character_voices[character] = selected_voice
    
    # Scene breakdown
    st.subheader("Scene Breakdown")
    for scene in analysis.get("scenes", []):
        with st.expander(f"Scene {scene['id']}: {scene['name']}"):
            st.markdown(f"**Tone:** {scene.get('tone', 'Not specified')}")
            st.markdown(f"**Characters:** {', '.join(scene.get('characters', []))}")
            
            if scene.get('props'):
                st.markdown(f"**Props:** {', '.join(scene.get('props', []))}")
    
    # Character relationships
    st.subheader("Character Relationships")
    for relationship in analysis.get("relationships", []):
        st.markdown(f"**{' & '.join(relationship.get('characters', []))}:** {relationship.get('relationship', 'Unknown')}")


def audio_generation_page():
    """Page for generating audio from dialogue"""
    st.header("Audio Generation")
    
    if st.session_state.dialogues == []:
        st.warning("Please upload and process a script first.")
        return
    
    # Controls for batch generation
    st.subheader("Batch Audio Generation")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Generate All Dialogue Audio"):
            with st.spinner("Generating audio for all dialogue lines..."):
                progress_bar = st.progress(0)
                
                for i, dialogue in enumerate(st.session_state.dialogues):
                    character = dialogue["character"]
                    text = dialogue["text"]
                    emotion = dialogue.get("emotion", "neutral")
                    
                    # Generate unique key for this dialogue
                    dialogue_key = f"{character}_{i}"
                    
                    if dialogue_key not in st.session_state.audio_clips:
                        audio_url = generate_audio_for_line(character, text, emotion)
                        st.session_state.audio_clips[dialogue_key] = {
                            "url": audio_url,
                            "character": character,
                            "text": text,
                            "emotion": emotion,
                            "scene_id": dialogue.get("scene_id", 1)
                        }
                    
                    # Update progress
                    progress_bar.progress((i + 1) / len(st.session_state.dialogues))
                
                st.success(f"Generated audio for {len(st.session_state.dialogues)} dialogue lines!")
    
    with col2:
        if st.button("Clear All Generated Audio", disabled=not st.session_state.audio_clips):
            st.session_state.audio_clips = {}
            st.success("All audio clips cleared!")
    
    # Individual dialogue processing
    st.subheader("Individual Dialogue Lines")
    
    for i, dialogue in enumerate(st.session_state.dialogues):
        dialogue_key = f"{dialogue['character']}_{i}"
        
        with st.expander(f"{dialogue['character']}: {dialogue['text'][:50]}{'...' if len(dialogue['text']) > 50 else ''}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Character:** {dialogue['character']}")
                st.markdown(f"**Text:** {dialogue['text']}")
                st.markdown(f"**Scene:** {dialogue.get('scene_id', 1)}")
                
                # Emotion selection
                emotions = ["neutral", "happy", "sad", "angry", "fearful", "surprised"]
                selected_emotion = st.selectbox(
                    "Select Emotion",
                    options=emotions,
                    index=emotions.index(dialogue.get("emotion", "neutral")),
                    key=f"emotion_select_{i}"
                )
                dialogue["emotion"] = selected_emotion
            
            with col2:
                # Generate button for this line
                if st.button("Generate Audio", key=f"gen_btn_{i}"):
                    audio_url = generate_audio_for_line(
                        dialogue["character"], 
                        dialogue["text"], 
                        dialogue["emotion"]
                    )
                    
                    st.session_state.audio_clips[dialogue_key] = {
                        "url": audio_url,
                        "character": dialogue["character"],
                        "text": dialogue["text"],
                        "emotion": dialogue["emotion"],
                        "scene_id": dialogue.get("scene_id", 1)
                    }
                    
                    st.success("Audio generated!")
                    st.rerun()
                
                # Display audio if available
                if dialogue_key in st.session_state.audio_clips:
                    audio_data = st.session_state.audio_clips[dialogue_key]
                    display_audio_player(audio_data["url"], audio_data["character"], audio_data["text"][:30] + "...")


def scene_playback_page():
    """Page for playing back scenes with generated audio"""
    st.header("Scene Playback")
    
    if not st.session_state.audio_clips:
        st.warning("Please generate audio for dialogue lines first.")
        return
    
    if not st.session_state.script_analysis:
        st.warning("Please upload and process a script first.")
        return
    
    # Scene selection
    scenes = st.session_state.script_analysis.get("scenes", [])
    scene_options = [f"Scene {scene['id']}: {scene['name']}" for scene in scenes]
    
    if not scene_options:
        scene_options = ["All Dialogue"]
    
    selected_scene = st.selectbox(
        "Select Scene to Play",
        options=["All Dialogue"] + scene_options
    )
    
    # Filter audio clips by scene if needed
    scene_id = None
    if selected_scene != "All Dialogue":
        scene_id = int(selected_scene.split(":")[0].replace("Scene ", ""))
    
    # Display playback controls
    st.subheader("Playback")
    
    # Get dialogue clips for selected scene
    scene_clips = []
    for key, clip in st.session_state.audio_clips.items():
        if scene_id is None or clip.get("scene_id") == scene_id:
            scene_clips.append(clip)
    
    # Sort clips (this would be by timestamp/order in real implementation)
    scene_clips = sorted(scene_clips, key=lambda x: x.get("scene_id", 0))
    
    if not scene_clips:
        st.info("No audio clips available for this scene.")
        return
    
    # Play all button
    if st.button("Play All Scene Audio"):
        st.info("In a production version, this would play all audio clips sequentially.")
        
        # In production, this would use JavaScript to chain audio playback
        for clip in scene_clips:
            with st.expander(f"{clip['character']}", expanded=True):
                display_audio_player(clip["url"], clip["character"], clip["text"])
    
    # Individual clip playback
    st.subheader("Scene Dialogue")
    for clip in scene_clips:
        with st.expander(f"{clip['character']}: {clip['text'][:50]}{'...' if len(clip['text']) > 50 else ''}"):
            st.markdown(f"**Character:** {clip['character']}")
            st.markdown(f"**Emotion:** {clip['emotion']}")
            st.markdown(f"**Text:** {clip['text']}")
            display_audio_player(clip["url"], clip["character"], clip["text"])
            
            # In production version, options to adjust timing, add SFX, etc.
            if st.checkbox("Show Advanced Options", key=f"adv_opt_{clip['character']}_{hash(clip['text'][:20])}"):
                st.slider("Speed", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
                st.slider("Volume", min_value=0.0, max_value=1.0, value=1.0, step=0.1)
                st.multiselect("Background SFX", options=["None", "Rain", "City Noise", "Wind", "Crowd"])


def project_management_page():
    """Page for managing projects"""
    st.header("Project Management")
    
    # Save current project
    st.subheader("Save Current Project")
    
    project_name = st.text_input("Project Name", 
                              value=f"Script Project {datetime.now().strftime('%Y-%m-%d')}")
    
    if st.button("Save Project", disabled=st.session_state.current_script is None):
        save_project(project_name)
    
    # View saved projects
    st.subheader("Saved Projects")
    
    if not st.session_state.projects:
        st.info("No saved projects yet.")
    else:
        for i, project in enumerate(st.session_state.projects):
            with st.expander(f"{project['name']} - {project['date']}"):
                st.markdown(f"**Script:** {project['script_name']}")
                st.markdown(f"**Characters:** {len(project.get('analysis', {}).get('characters', []))}")
                st.markdown(f"**Audio Clips:** {len(project.get('audio_clips', {}))}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Load Project", key=f"load_project_{i}"):
                        st.session_state.current_script = type('obj', (object,), {'name': project['script_name']})
                        st.session_state.script_analysis = project['analysis']
                        st.session_state.dialogues = project['dialogues']
                        st.session_state.audio_clips = project['audio_clips']
                        st.session_state.character_voices = project['character_voices']
                        
                        st.success(f"Project '{project['name']}' loaded successfully!")
                        st.rerun()
                
                with col2:
                    if st.button("Delete Project", key=f"delete_project_{i}"):
                        st.session_state.projects.pop(i)
                        st.success(f"Project deleted!")
                        st.rerun()
    
    # Export/Import functionality (simplified for demo)
    st.subheader("Export/Import")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export Current Project", disabled=st.session_state.current_script is None):
            # In production, this would create a downloadable JSON file
            st.info("In production, this would allow downloading the project as a JSON file.")
    
    with col2:
        uploaded_file = st.file_uploader("Import Project", type=['json'])
        
        if uploaded_file is not None:
            if st.button("Load Imported Project"):
                # In production, this would parse the JSON file and load the project
                st.info("In production, this would load the project from the uploaded JSON file.")


# Main app
def main():
    """Main application function"""
    # Header with logo
    st.title("🎬 AI Script Reader Platform")
    
    # Get current menu selection
    menu = sidebar_menu()
    
    # Display selected page
    if menu == "Upload Script":
        upload_script_page()
    elif menu == "Script Analysis":
        script_analysis_page()
    elif menu == "Audio Generation":
        audio_generation_page()
    elif menu == "Scene Playback":
        scene_playback_page()
    elif menu == "Project Management":
        project_management_page()


if __name__ == "__main__":
    main()