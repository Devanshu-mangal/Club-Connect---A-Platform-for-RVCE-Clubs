import streamlit as st
import datetime
import hashlib
import json
import os
from PIL import Image
import io
import base64

# Session state initialization
if 'general_posts' not in st.session_state:
    st.session_state.general_posts = []

if 'club_posts' not in st.session_state:
    st.session_state.club_posts = {
        'Alaap': [], 'CARV Access': [], 'CARV English': [], 'CARV Hindi': [], 'CARV Kannada': [], 'Dastaan': [], 
        'Evoke': [], 'footprints': [], 'ASHWA RACING': [], 'Coding Club': [], 'DEB-SOC': [], 'FREQUENCY CLUB': [], 'Photography Club': [],'PROJECT JATAYU': [], 'RAAG': [], 'Rotaract Club of RVCE': [], 'RV Quiz Corp': [], 'RVCE HAM CLUB': [],
        'SOLAR CAR TEAM': [], 'TEAM ANTARIKSH': [], 'TEAM ASTRA': [], 'TEAM CHIMERA': [], 'Team Dhruva': [],
        'TEAM GARUDA': [], 'TEAM HELIOS': [], 'TEAM HYDRA': [], 'TEAM KRUSHI': [], 'TEAM VYOMA': []
    }

POSTS_FILE = 'posts.json'

def image_to_base64(image):
    """Convert PIL Image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def load_posts():
    if os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, 'r') as file:
            data = json.load(file)
            st.session_state.general_posts = data.get('general', [])
            for club in st.session_state.club_posts:
                if club not in data.get('clubs', {}):
                    data['clubs'][club] = []
            st.session_state.club_posts = data.get('clubs', {})

def save_posts():
    data = {
        'general': st.session_state.general_posts,
        'clubs': st.session_state.club_posts
    }
    with open(POSTS_FILE, 'w') as file:
        json.dump(data, file)

load_posts()

sorted_clubs = [
    'Alaap', 'CARV Access', 'CARV English', 'CARV Hindi', 'CARV Kannada', 'Dastaan', 'Evoke', 'footprints',
    'ASHWA RACING', 'Coding Club', 'DEB-SOC', 'FREQUENCY CLUB', 'Photography Club', 'PROJECT JATAYU', 'RAAG',
    'Rotaract Club of RVCE', 'RV Quiz Corp', 'RVCE HAM CLUB', 'SOLAR CAR TEAM', 'TEAM ANTARIKSH', 'TEAM ASTRA',
    'TEAM CHIMERA', 'Team Dhruva', 'TEAM GARUDA', 'TEAM HELIOS', 'TEAM HYDRA', 'TEAM KRUSHI', 'TEAM VYOMA'
]

CLUB_CREDENTIALS = {
    club: {'username': f"{club.lower().replace(' ', '_')}_admin", 
           'password': hashlib.sha256(f"{club.lower().replace(' ', '_')}123".encode()).hexdigest()}
    for club in sorted_clubs
}

# Session state initialization for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'current_club' not in st.session_state:
    st.session_state.current_club = None

def verify_credentials(club, username, password):
    if club in CLUB_CREDENTIALS:
        correct_username = CLUB_CREDENTIALS[club]['username']
        correct_password = CLUB_CREDENTIALS[club]['password']
        return (username == correct_username and 
                hashlib.sha256(password.encode()).hexdigest() == correct_password)
    return False

def like_post(feed_type, post_idx, club_name=None):
    if feed_type == 'general':
        st.session_state.general_posts[post_idx]['likes'] += 1
    elif feed_type == 'club' and club_name:
        st.session_state.club_posts[club_name][post_idx]['likes'] += 1
    save_posts()

def add_post(feed_type, club_name=None):
    post_text = st.session_state.get(f'new_post' if club_name is None else f'new_club_post_{club_name}', '')
    image_file = st.session_state.get(f'new_post_image' if club_name is None else f'new_club_post_image_{club_name}')
    
    if post_text or image_file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        post = {
            'text': post_text,
            'timestamp': timestamp,
            'likes': 0,
            'source': club_name if club_name else "General",
            'id': hashlib.md5(f"{timestamp}{post_text}".encode()).hexdigest()
        }
        
        # Handle image if uploaded
        if image_file:
            image = Image.open(image_file)
            # Resize image to reasonable dimensions if needed
            max_size = (800, 800)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            post['image'] = image_to_base64(image)

        if feed_type == 'general':
            st.session_state.general_posts.insert(0, post)
        elif feed_type == 'club' and club_name:
            st.session_state.club_posts[club_name].insert(0, post)
            post_copy = post.copy()
            st.session_state.general_posts.insert(0, post_copy)

        save_posts()
        # Clear the form
        st.session_state[f'new_post' if club_name is None else f'new_club_post_{club_name}'] = ''
        if f'new_post_image' in st.session_state:
            del st.session_state[f'new_post_image']
        if f'new_club_post_image_{club_name}' in st.session_state:
            del st.session_state[f'new_club_post_image_{club_name}']

def share_to_general(club_name, post):
    if post not in st.session_state.general_posts:
        post_copy = post.copy()
        st.session_state.general_posts.insert(0, post_copy)
        save_posts()
        st.success("Post shared to general feed successfully!")
    else:
        st.warning("This post is already in the general feed!")

def delete_post(feed_type, post_idx, club_name=None):
    if feed_type == 'club' and club_name:
        if 0 <= post_idx < len(st.session_state.club_posts[club_name]):
            post_to_delete = st.session_state.club_posts[club_name][post_idx]
            post_id = post_to_delete.get('id')
            
            del st.session_state.club_posts[club_name][post_idx]
            
            st.session_state.general_posts = [
                post for post in st.session_state.general_posts 
                if post.get('id') != post_id
            ]
            
            save_posts()
            st.success(f"Post deleted from both {club_name} and general feed!")
            st.rerun()
    
    elif feed_type == 'general':
        if 0 <= post_idx < len(st.session_state.general_posts):
            post_to_delete = st.session_state.general_posts[post_idx]
            post_id = post_to_delete.get('id')
            source_club = post_to_delete.get('source')
            
            del st.session_state.general_posts[post_idx]
            
            if source_club in st.session_state.club_posts:
                st.session_state.club_posts[source_club] = [
                    post for post in st.session_state.club_posts[source_club] 
                    if post.get('id') != post_id
                ]
            
            save_posts()
            st.success("Post deleted successfully!")
            st.rerun()

# Custom CSS for enhanced styling
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .college-name {
        font-size: 1.2rem;
        color: #f0f0f0;
        margin-bottom: 0.5rem;
    }
    .app-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .welcome-section {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .role-selector {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .continue-btn {
        background-color: #1e3c72;
        color: white;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        border: none;
        cursor: pointer;
        text-align: center;
        margin-top: 1rem;
    }
    .continue-btn:hover {
        background-color: #2a5298;
    }
    .college-logo {
        width: 100px;
        height: 100px;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# College logo URL (replace with actual RVCE logo path)
logo_url = "https://rvce.edu.in/sites/default/files/logo_new.png"

# Main landing page content
st.markdown("""
    <div class="main-header">
        <img src="https://rvce.edu.in/sites/default/files/logo_new.png" class="college-logo">
        <div class="college-name">RV COLLEGE OF ENGINEERING</div>
        <div class="app-title">🌟 RV SOCIAL CONNECT</div>
        <div style="font-size: 1.1rem;">Go Change The World</div>
        <div style="font-size: 1.1rem;">Connecting Minds, Bridging Communities</div>
    </div>
""", unsafe_allow_html=True)

if not st.session_state.user_type:
    st.markdown("""
        <div class="welcome-section">
            <h2 style="color: #1e3c72; margin-bottom: 1rem;">👋 Welcome to RV Connect!</h2>
            <p style="color: #666; margin-bottom: 2rem;">
                Join our vibrant community platform designed exclusively for RVCE members. 
                Share updates, stay connected with clubs, and be part of the RVCE digital ecosystem.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Role selection section
    st.markdown('<div class="role-selector">', unsafe_allow_html=True)
    st.markdown('#### Select your role to continue')
    user_type = st.radio(
        "",  # Empty label since we're using custom header
        ["Student", "Staff", "Club Board Member"],
        format_func=lambda x: {
            "Student": "🎓 Student",
            "Staff": "👨‍🏫 Staff",
            "Club Board Member": "🎭 Club Board Member"
        }[x]
    )
    
    # Custom styled continue button
    if st.button("Continue", key="continue_btn"):
        st.session_state.user_type = user_type
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Footer with additional information
    st.markdown("""
        <div style="text-align: center; margin-top: 2rem; padding: 1rem; color: #666;">
            <p style="font-size: 0.9rem;">
                © 2025 RV College of Engineering<br>
                Mysuru Road, RV Vidyaniketan Post, Bengaluru-560059
            </p>
        </div>
    """, unsafe_allow_html=True)

elif st.session_state.user_type == "Club Board Member" and not st.session_state.authenticated:
    st.header("🔐 Club Board Member Login")
    
    selected_club = st.selectbox("Select your club:", sorted_clubs)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if verify_credentials(selected_club, username, password):
            st.session_state.authenticated = True
            st.session_state.current_club = selected_club
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials!")

else:
    tab1, tab2, tab3 = st.tabs(["General Feed", "Club Feeds", "Staff Section"])

    with tab1:
        st.header("📱 General Feed")
        
        for idx, post in enumerate(st.session_state.general_posts):
            with st.container():
                st.markdown(f"---")
                st.write(f"🕒 {post['timestamp']}")
                if 'source' in post:
                    st.write(f"📍 Posted from: {post['source']}")
                st.write(post['text'])
                if 'image' in post:
                    st.image(base64.b64decode(post['image']))
                col1, col2 = st.columns([1, 9])
                with col1:
                    st.button(f"❤️ {post['likes']}", key=f"like_general_{idx}", 
                             on_click=like_post, args=('general', idx))
                
                if (st.session_state.user_type == "Club Board Member" and 
                    st.session_state.authenticated and 
                    post.get('source') == st.session_state.current_club):
                    with col2:
                        st.button("🗑️ Delete", key=f"delete_general_{idx}",
                                 on_click=delete_post, args=('general', idx))
    
    with tab2:
        st.header("🎭 Club Feeds")
        
        if st.session_state.user_type == "Club Board Member":
            selected_club = st.session_state.current_club
            st.subheader(f"📌 {selected_club}")
        else:
            selected_club = st.selectbox("Select a Club", sorted_clubs)
        
        if st.session_state.user_type == "Club Board Member" and st.session_state.authenticated:
            st.text_area("Create a new club post:", key=f'new_club_post_{selected_club}', height=100)
            st.file_uploader("Add an image to your post:", type=['png', 'jpg', 'jpeg'], 
                           key=f'new_club_post_image_{selected_club}')
            col1, col2 = st.columns(2)
            with col1:
                st.button("Post to Club", key=f"share_club_{selected_club}", 
                         on_click=add_post, args=('club', selected_club))
            with col2:
                if st.session_state.get(f'new_club_post_{selected_club}'):
                    if st.button("Share to General Feed", key=f"share_general_{selected_club}"):
                        add_post('general', selected_club)
        
        for idx, post in enumerate(st.session_state.club_posts[selected_club]):
            with st.container():
                st.markdown(f"---")
                st.write(f"🕒 {post['timestamp']}")
                st.write(post['text'])
                if 'image' in post:
                    st.image(base64.b64decode(post['image']))
                col1, col2, col3 = st.columns([1, 8, 1])
                with col1:
                    st.button(f"❤️ {post['likes']}", 
                             key=f"like_club_{selected_club}_{idx}",
                             on_click=like_post, 
                             args=('club', idx, selected_club))
                if st.session_state.user_type == "Club Board Member" and st.session_state.authenticated:
                    with col2:
                        st.button("📢 Share to General", 
                                key=f"share_existing_{selected_club}_{idx}",
                                on_click=share_to_general,
                                args=(selected_club, post))
                    with col3:
                        st.button("🗑️ Delete", 
                                key=f"delete_club_{selected_club}_{idx}",
                                on_click=delete_post,
                                args=('club', idx, selected_club))
    
    with tab3:
        st.header("👩‍🏫 Staff Section")
        st.write("This section is under development.")

    if st.session_state.user_type == "Club Board Member" and st.session_state.authenticated:
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user_type = None
            st.session_state.current_club = None
            st.rerun()

    with st.sidebar:
        pass