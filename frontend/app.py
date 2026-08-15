"""
EnterpriseAssist AI - Streamlit User Interface
==============================================

This module provides the frontend interface for the EnterpriseAssist AI application.
It strictly adheres to a minimalist, monochrome visual design system while preserving
all underlying connection logic to the backend AI core and authentication systems.

Design System Specifications:
- Monochrome Palette: #000000 (Black), #FFFFFF (White), Grays (#F9FAFB to #D1D5DB).
- Typography: System sans-serif stack, regular weight preferred, minimal boldness.
- Geometry: Flat, 2px-3px border radii (sharp/minimalist), 1px solid borders.
- Components: Full-width buttons, uncontained chat inputs, no gradients or shadows.
"""

import streamlit as st
import requests
from backend.ai_core import get_ai_response


class EnterpriseThemeManager:
    """
    A dedicated class to manage and generate the strict monochrome styling 
    required by the EnterpriseAssist design system. This class builds a highly 
    verbose, extensively prefixed CSS string to ensure absolute cross-browser 
    compatibility and strict enforcement of the visual rules.
    """

    def __init__(self):
        # ---------------------------------------------------------
        # COLOR PALETTE (Strictly Monochrome)
        # ---------------------------------------------------------
        self.color_black = "#000000"
        self.color_white = "#FFFFFF"
        self.color_bg_main = "#FAFAFA"  # Soft off-white for the main app area
        self.color_bg_sidebar = "#F3F4F6"  # Slightly darker off-white for sidebar contrast
        self.color_border_light = "#D1D5DB"  # Thin 1px light gray
        self.color_border_focus = "#9CA3AF"  # Slightly darker gray for input focus
        
        self.text_primary = "#111827"
        self.text_secondary = "#4B5563"
        self.text_tertiary = "#6B7280"
        self.text_muted = "#9CA3AF"

        # ---------------------------------------------------------
        # TYPOGRAPHY
        # ---------------------------------------------------------
        self.font_family_base = (
            '"Inter", system-ui, -apple-system, BlinkMacSystemFont, '
            '"Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
        )
        self.font_family_mono = (
            '"SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, monospace'
        )
        
        self.font_size_h1 = "3rem"
        self.font_size_h2 = "1.5rem"
        self.font_size_body = "0.95rem"
        self.font_size_small = "0.85rem"
        self.font_size_micro = "0.65rem"

        self.font_weight_regular = "400"
        self.font_weight_medium = "500"
        self.font_weight_bold = "700"

        # ---------------------------------------------------------
        # GEOMETRY & SPACING
        # ---------------------------------------------------------
        self.border_radius_standard = "2px"
        self.border_radius_round = "50%"
        self.border_width_standard = "1px"
        self.border_style_standard = "solid"
        
        self.spacing_padding_main = "1.5rem 3rem 2rem 3rem"
        self.spacing_padding_input = "0.6rem 0.8rem"
        self.spacing_padding_button = "0.6rem 1rem"
        self.spacing_padding_chat_bubble = "0.9rem 1.1rem"
        
        self.chat_avatar_size = "2.2rem"

    def get_reset_styles(self) -> str:
        """Generates standard CSS resets and hidden Streamlit defaults."""
        return f"""
        /* --- 1. GLOBAL RESETS --- */
        * {{
            -webkit-box-sizing: border-box !important;
            -moz-box-sizing: border-box !important;
            box-sizing: border-box !important;
        }}

        html, body {{
            margin: 0;
            padding: 0;
            background-color: {self.color_bg_main} !important;
            color: {self.text_primary} !important;
            font-family: {self.font_family_base} !important;
            -webkit-font-smoothing: antialiased !important;
            -moz-osx-font-smoothing: grayscale !important;
        }}

        /* Hide unnecessary Streamlit artifacts to maintain minimalist UI */
        /* Targets ONLY the Deploy button and Main Menu to prevent layout collapse */
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"],
        [data-testid="stAppDeployButton"],
        .stAppDeployButton,
        #MainMenu,
        footer {{
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }}
        """

    def get_layout_styles(self) -> str:
        """Generates styles for the main layout containers."""
        return f"""
        /* --- 2. MAIN APPLICATION LAYOUT --- */
        .stApp {{
            background-color: {self.color_bg_main} !important;
        }}

        [data-testid="stMain"] {{
            background-color: {self.color_bg_main} !important;
        }}

        [data-testid="stMain"] .block-container,
        .main .block-container {{
            padding: {self.spacing_padding_main} !important;
            max-width: 100% !important;
            width: 100% !important;
        }}
        """

    def get_sidebar_styles(self) -> str:
        """
        Generates styles for the sidebar and critical toggle controls.
        Ensures the header wrapper remains active so the toggle is consistently visible.
        """
        return f"""
        /* --- 3. SIDEBAR & NAVIGATION --- */
        
        /* Ensure the header container is completely transparent but active */
        [data-testid="stHeader"] {{
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
        }}

        /* Style the actual toggle button without overriding its native placement */
        [data-testid="collapsedControl"] {{
            display: -webkit-box !important;
            display: -ms-flexbox !important;
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            background-color: {self.color_white} !important;
            border: {self.border_width_standard} {self.border_style_standard} {self.color_border_light} !important;
            border-radius: {self.border_radius_standard} !important;
            color: {self.color_black} !important;
            -webkit-transition: none !important;
            -o-transition: none !important;
            transition: none !important;
            z-index: 100000 !important;
        }}
        
        [data-testid="collapsedControl"]:hover {{
            background-color: {self.color_bg_sidebar} !important;
        }}

        /* Force the SVG icon inside the toggle to be black */
        [data-testid="collapsedControl"] svg {{
            fill: {self.color_black} !important;
            stroke: {self.color_black} !important;
        }}

        /* Style the close button when the sidebar is open */
        [data-testid="stSidebarCollapseButton"] {{
            color: {self.color_black} !important;
            background-color: transparent !important;
        }}
        
        [data-testid="stSidebarCollapseButton"]:hover {{
            background-color: {self.color_border_light} !important;
        }}
        
        [data-testid="stSidebarCollapseButton"] svg {{
            fill: {self.color_black} !important;
            stroke: {self.color_black} !important;
        }}

        /* The Sidebar Panel */
        [data-testid="stSidebar"] {{
            background-color: {self.color_bg_sidebar} !important;
            border-right: {self.border_width_standard} {self.border_style_standard} {self.color_border_light} !important;
            min-width: 300px !important;
        }}
        
        [data-testid="stSidebar"] > div:first-child {{
            background-color: {self.color_bg_sidebar} !important;
        }}

        .sidebar-section-label {{
            font-family: {self.font_family_mono};
            font-size: {self.font_size_micro};
            font-weight: {self.font_weight_bold};
            letter-spacing: 0.15em;
            text-transform: uppercase;
            color: {self.text_tertiary};
            margin-bottom: 1rem;
            margin-top: 1.5rem;
            display: block;
        }}
        
        .sidebar-section-label:first-of-type {{
            margin-top: 0;
        }}

        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
            color: {self.text_primary} !important;
            font-size: {self.font_size_small} !important;
            font-weight: {self.font_weight_medium} !important;
            margin-bottom: 0.2rem !important;
        }}
        """

    def get_input_styles(self) -> str:
        """Generates styles for all text inputs (login, passwords, generic)."""
        return f"""
        /* --- 4. FORM INPUTS --- */
        [data-testid="stTextInput"] div[data-baseweb="input"],
        [data-testid="stTextInput"] input {{
            background-color: {self.color_white} !important;
            border-radius: {self.border_radius_standard} !important;
            border: none !important; /* Managed by wrapper below */
            color: {self.text_primary} !important;
            font-size: {self.font_size_body} !important;
            font-family: {self.font_family_base} !important;
            -webkit-box-shadow: none !important;
            box-shadow: none !important;
            -webkit-transition: none !important;
            -o-transition: none !important;
            transition: none !important;
        }}
        
        [data-testid="stTextInput"] div[data-baseweb="base-input"] {{
            background-color: {self.color_white} !important;
            border: {self.border_width_standard} {self.border_style_standard} {self.color_border_light} !important;
            border-radius: {self.border_radius_standard} !important;
        }}

        [data-testid="stTextInput"] div[data-baseweb="base-input"]:focus-within {{
            border-color: {self.color_border_focus} !important;
            -webkit-box-shadow: none !important;
            box-shadow: none !important;
        }}

        [data-testid="stTextInput"] input::-webkit-input-placeholder {{ color: {self.text_muted} !important; }}
        [data-testid="stTextInput"] input::-moz-placeholder          {{ color: {self.text_muted} !important; }}
        [data-testid="stTextInput"] input:-ms-input-placeholder      {{ color: {self.text_muted} !important; }}
        [data-testid="stTextInput"] input::-ms-input-placeholder     {{ color: {self.text_muted} !important; }}
        [data-testid="stTextInput"] input::placeholder               {{ color: {self.text_muted} !important; }}
        """

    def get_button_styles(self) -> str:
        """Generates styles for all buttons, ensuring they are identical blocks of black."""
        return f"""
        /* --- 5. BUTTONS (Uniform Black Blocks) --- */
        .stButton {{
            width: 100% !important;
            display: -webkit-box !important;
            display: -ms-flexbox !important;
            display: flex !important;
        }}

        .stButton > button {{
            background-color: {self.color_black} !important;
            color: {self.color_white} !important;
            border: {self.border_width_standard} {self.border_style_standard} {self.color_black} !important;
            border-radius: {self.border_radius_standard} !important;
            font-family: {self.font_family_base} !important;
            font-weight: {self.font_weight_medium} !important;
            font-size: {self.font_size_body} !important;
            padding: {self.spacing_padding_button} !important;
            width: 100% !important;
            min-height: 2.5rem !important;
            display: -webkit-box !important;
            display: -ms-flexbox !important;
            display: flex !important;
            -webkit-box-pack: center !important;
            -ms-flex-pack: center !important;
            justify-content: center !important;
            -webkit-box-align: center !important;
            -ms-flex-align: center !important;
            align-items: center !important;
            -webkit-box-shadow: none !important;
            box-shadow: none !important;
            -webkit-transition: none !important;
            -o-transition: none !important;
            transition: none !important;
            cursor: pointer !important;
        }}

        .stButton > button:hover,
        .stButton > button:active,
        .stButton > button:focus {{
            background-color: {self.text_primary} !important;
            color: {self.color_white} !important;
            border-color: {self.text_primary} !important;
            -webkit-transform: none !important;
            -ms-transform: none !important;
            transform: none !important;
            -webkit-box-shadow: none !important;
            box-shadow: none !important;
        }}

        .stButton > button p {{
            color: inherit !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        """

    def get_chat_input_styles(self) -> str:
        """Generates strictly uncontained, sharp chat input styling."""
        return f"""
        /* --- 6. CHAT INPUT BAR --- */
        
        /* Remove the generic bottom bar block so it sits directly on background */
        [data-testid="stBottomBlockContainer"],
        [data-testid="stBottom"] {{
            background-color: transparent !important;
            background: transparent !important;
            border-top: none !important;
            padding: 1rem 3rem !important;
            max-width: 100% !important;
        }}
        
        [data-testid="stChatInput"] {{
            background-color: transparent !important;
            background: transparent !important;
        }}
        
        /* Inner Chat Container */
        [data-testid="stChatInput"] > div {{
            background-color: {self.color_white} !important;
            border: {self.border_width_standard} {self.border_style_standard} {self.color_border_light} !important;
            border-radius: {self.border_radius_standard} !important;
            -webkit-box-shadow: none !important;
            box-shadow: none !important;
            padding: 0.2rem !important;
        }}
        
        [data-testid="stChatInput"] textarea {{
            background-color: transparent !important;
            color: {self.text_primary} !important;
            border: none !important;
            font-family: {self.font_family_base} !important;
            font-size: {self.font_size_body} !important;
            padding: 0.6rem !important;
            -webkit-box-shadow: none !important;
            box-shadow: none !important;
        }}
        
        [data-testid="stChatInput"] textarea:focus {{
            outline: none !important;
            -webkit-box-shadow: none !important;
            box-shadow: none !important;
        }}

        [data-testid="stChatInput"] textarea::-webkit-input-placeholder {{ color: {self.text_muted} !important; }}
        [data-testid="stChatInput"] textarea::-moz-placeholder          {{ color: {self.text_muted} !important; }}
        [data-testid="stChatInput"] textarea:-ms-input-placeholder      {{ color: {self.text_muted} !important; }}
        [data-testid="stChatInput"] textarea::-ms-input-placeholder     {{ color: {self.text_muted} !important; }}
        [data-testid="stChatInput"] textarea::placeholder               {{ color: {self.text_muted} !important; }}

        /* Chat Send Button */
        [data-testid="stChatInputSubmitButton"] {{
            background-color: {self.color_black} !important;
            border-radius: {self.border_radius_standard} !important;
            border: none !important;
            -webkit-box-shadow: none !important;
            box-shadow: none !important;
            height: 100% !important;
            margin: 0 !important;
            padding: 0.4rem !important;
        }}
        
        [data-testid="stChatInputSubmitButton"] svg {{
            fill: {self.color_white} !important;
            stroke: {self.color_white} !important;
        }}
        
        [data-testid="stChatInputSubmitButton"]:hover {{
            background-color: {self.text_primary} !important;
        }}
        """

    def get_custom_html_styles(self) -> str:
        """Generates styles for manually injected HTML components (status, bubbles, headers)."""
        return f"""
        /* --- 7. CUSTOM INJECTED HTML COMPONENTS --- */
        
        /* Status Indicator in Sidebar */
        .sidebar-status {{
            display: -webkit-box;
            display: -ms-flexbox;
            display: flex;
            -webkit-box-align: center;
            -ms-flex-align: center;
            align-items: center;
            gap: 0.6rem;
            margin-top: 1rem;
            padding: 0.8rem 0;
            font-size: {self.font_size_small};
        }}
        
        .sidebar-status-dot {{
            width: 0.5rem;
            height: 0.5rem;
            background-color: {self.color_black};
            border-radius: {self.border_radius_round};
            display: inline-block;
        }}
        
        .sidebar-status-label {{
            font-family: {self.font_family_mono};
            font-size: {self.font_size_micro};
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: {self.text_secondary};
            font-weight: {self.font_weight_bold};
        }}
        
        .sidebar-status-value {{
            font-weight: {self.font_weight_medium};
            color: {self.color_black};
        }}

        /* Headers and Typography Components */
        .header-eyebrow {{
            font-family: {self.font_family_mono};
            font-size: 0.7rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: {self.text_tertiary};
            margin-bottom: 0.8rem;
            font-weight: {self.font_weight_medium};
            display: block;
        }}
        
        .page-title {{
            font-family: {self.font_family_base};
            font-size: {self.font_size_h1};
            font-weight: {self.font_weight_bold};
            letter-spacing: -0.03em;
            margin: 0 0 0.3rem 0;
            color: {self.color_black};
            line-height: 1.1;
            -webkit-animation: fadeSlideIn 0.4s ease;
            animation: fadeSlideIn 0.4s ease;
        }}
        
        .page-subtitle {{
            font-family: {self.font_family_base};
            font-size: 1rem;
            color: {self.text_tertiary};
            margin: 0 0 1.5rem 0;
            font-weight: {self.font_weight_regular};
        }}
        
        .page-divider {{
            width: 3rem;
            height: 1px;
            background-color: {self.color_border_light};
            margin: 1.5rem 0 2rem 0;
            display: block;
        }}

        /* Chat Message Bubbles */
        @-webkit-keyframes fadeSlideIn {{
            from {{ opacity: 0; -webkit-transform: translateY(4px); transform: translateY(4px); }}
            to {{ opacity: 1; -webkit-transform: translateY(0); transform: translateY(0); }}
        }}
        @keyframes fadeSlideIn {{
            from {{ opacity: 0; -webkit-transform: translateY(4px); transform: translateY(4px); }}
            to {{ opacity: 1; -webkit-transform: translateY(0); transform: translateY(0); }}
        }}
        
        .chat-message {{
            display: -webkit-box;
            display: -ms-flexbox;
            display: flex;
            gap: 0.8rem;
            margin: 1rem 0;
            -webkit-box-align: start;
            -ms-flex-align: start;
            align-items: flex-start;
            -webkit-animation: fadeSlideIn 0.3s ease;
            animation: fadeSlideIn 0.3s ease;
            width: 100%;
        }}
        
        .chat-avatar {{
            display: -webkit-box;
            display: -ms-flexbox;
            display: flex;
            -webkit-box-align: center;
            -ms-flex-align: center;
            align-items: center;
            -webkit-box-pack: center;
            -ms-flex-pack: center;
            justify-content: center;
            width: {self.chat_avatar_size};
            height: {self.chat_avatar_size};
            min-width: {self.chat_avatar_size};
            border-radius: {self.border_radius_standard};
            font-weight: {self.font_weight_medium};
            font-size: 0.75rem;
            letter-spacing: 0.05em;
            font-family: {self.font_family_mono};
        }}
        
        .chat-avatar.user {{
            background-color: {self.color_black};
            color: {self.color_white};
            border: none;
        }}
        
        .chat-avatar.assistant {{
            background-color: {self.color_white};
            color: {self.color_black};
            border: {self.border_width_standard} {self.border_style_standard} {self.color_border_light};
        }}
        
        .chat-bubble {{
            -webkit-box-flex: 1;
            -ms-flex: 1;
            flex: 1;
            padding: {self.spacing_padding_chat_bubble};
            border-radius: {self.border_radius_standard};
            font-size: {self.font_size_body};
            line-height: 1.6;
            word-wrap: break-word;
            font-family: {self.font_family_base};
        }}
        
        .chat-bubble.user {{
            background-color: {self.color_black};
            color: {self.color_white};
            margin-left: auto;
            max-width: 80%;
            border: none;
        }}
        
        .chat-bubble.assistant {{
            background-color: {self.color_white};
            color: {self.color_black};
            border: {self.border_width_standard} {self.border_style_standard} {self.color_border_light};
            max-width: 85%;
        }}

        /* Loading Spinner styling */
        [data-testid="stSpinner"] p {{
            color: {self.text_secondary} !important;
            font-size: {self.font_size_small} !important;
            font-weight: {self.font_weight_regular} !important;
            font-family: {self.font_family_base} !important;
        }}

        /* Scrollable Chat Area Border */
        .st-key-chat_scroll {{
            border: {self.border_width_standard} {self.border_style_standard} {self.color_border_light};
            border-radius: {self.border_radius_standard};
            padding: 0.5rem 1rem;
            background-color: {self.color_white};
        }}

        /* Responsive Media Queries */
        @media screen and (max-width: 768px) {{
            .page-title {{ font-size: 2rem; }}
            .chat-bubble.user, .chat-bubble.assistant {{ max-width: 100%; }}
            [data-testid="stMain"] .block-container,
            .main .block-container {{
                padding: 1rem !important;
            }}
        }}
        """

    def generate_full_css(self) -> str:
        """Aggregates all CSS blocks into a single payload."""
        css_blocks = [
            "<style>",
            self.get_reset_styles(),
            self.get_layout_styles(),
            self.get_sidebar_styles(),
            self.get_input_styles(),
            self.get_button_styles(),
            self.get_chat_input_styles(),
            self.get_custom_html_styles(),
            "</style>"
        ]
        return "\n".join(css_blocks)


# =====================================================================
# APP INITIALIZATION & CONFIGURATION
# =====================================================================

# Ensure initial_sidebar_state is "expanded" to aid visibility on mobile/smaller screens
st.set_page_config(
    page_title="EnterpriseAssist AI",
    page_icon="⬛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Instantiate the theme manager and inject the CSS payload immediately
theme_manager = EnterpriseThemeManager()
css_payload = theme_manager.generate_full_css()
st.markdown(css_payload, unsafe_allow_html=True)


# =====================================================================
# SESSION STATE MANAGEMENT
# =====================================================================
# We explicitly check and initialize all required state dictionaries.
# This prevents KeyErrors during live reload or deep linking.

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "employee_id" not in st.session_state:
    st.session_state.employee_id = None

if "employee_name" not in st.session_state:
    st.session_state.employee_name = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "genai_history" not in st.session_state:
    st.session_state.genai_history = []

if "pending_action" not in st.session_state:
    st.session_state.pending_action = None


# =====================================================================
# UI COMPONENTS: SIDEBAR (AUTHENTICATION & STATUS)
# =====================================================================

with st.sidebar:
    # ---------------------------------------------------------
    # STATE: LOGGED OUT
    # ---------------------------------------------------------
    if not st.session_state.logged_in:
        
        # Section Label
        st.markdown(
            '<div class="sidebar-section-label">Session Settings</div>', 
            unsafe_allow_html=True
        )

        # Input fields for authentication
        emp_id = st.text_input(
            label="Employee ID",
            key="emp_id"
        )
        
        password = st.text_input(
            label="Password", 
            type="password", 
            key="pwd"
        )

        # Authentication Button Trigger
        if st.button(label="Sign In", key="login_btn"):
            try:
                # Backend Authentication Call
                response = requests.post(
                    url="http://127.0.0.1:8000/login",
                    json={
                        "employee_id": emp_id, 
                        "password": password
                    },
                    timeout=10 # Added a small safety timeout
                )
                
                result = response.json()

                if result.get("success"):
                    # Hydrate session state on success
                    st.session_state.logged_in = True
                    st.session_state.employee_id = result["employee_id"]
                    st.session_state.employee_name = result["name"]
                    st.rerun()
                else:
                    st.error("Invalid credentials")
                    
            except requests.exceptions.RequestException as req_err:
                st.error(f"Network error: {str(req_err)}")
            except Exception as e:
                st.error(f"Connection error: {str(e)}")

    # ---------------------------------------------------------
    # STATE: LOGGED IN
    # ---------------------------------------------------------
    else:
        # Section Label
        st.markdown(
            '<div class="sidebar-section-label">Active Session</div>', 
            unsafe_allow_html=True
        )

        # User Profile Card
        # Left-aligned to prevent unintended Markdown code block rendering.
        profile_card_html = f"""
<div style="background-color: {theme_manager.color_white}; border: {theme_manager.border_width_standard} {theme_manager.border_style_standard} {theme_manager.color_border_light}; border-radius: {theme_manager.border_radius_standard}; padding: 1rem; margin-bottom: 1rem;">
    <div style="font-size: {theme_manager.font_size_micro}; letter-spacing: 0.1em; text-transform: uppercase; color: {theme_manager.text_secondary}; margin-bottom: 0.4rem; font-family: {theme_manager.font_family_mono}; font-weight: {theme_manager.font_weight_bold};">Employee</div>
    <div style="font-size: {theme_manager.font_size_body}; font-weight: {theme_manager.font_weight_medium}; color: {theme_manager.color_black}; margin-bottom: 0.6rem; font-family: {theme_manager.font_family_base};">{st.session_state.employee_name}</div>
    <div style="font-size: {theme_manager.font_size_micro}; letter-spacing: 0.1em; text-transform: uppercase; color: {theme_manager.text_secondary}; margin-bottom: 0.4rem; font-family: {theme_manager.font_family_mono}; font-weight: {theme_manager.font_weight_bold};">ID</div>
    <div style="font-size: 0.9rem; color: {theme_manager.color_black}; font-family: {theme_manager.font_family_mono};">{st.session_state.employee_id}</div>
</div>
"""
        st.markdown(profile_card_html, unsafe_allow_html=True)

        # Connection Status Indicator
        status_html = """
<div class="sidebar-status">
    <span class="sidebar-status-dot"></span>
    <span class="sidebar-status-label">Status</span>
    <span class="sidebar-status-value">Active</span>
</div>
"""
        st.markdown(status_html, unsafe_allow_html=True)

        # Logout Mechanism
        if st.button(label="Sign Out", key="logout_btn"):
            # Purge session state variables safely
            st.session_state.logged_in = False
            st.session_state.employee_id = None
            st.session_state.employee_name = None
            st.session_state.chat_history.clear()
            st.session_state.genai_history.clear()
            st.session_state.pending_action = None  # Prevents stale confirmations leaking
            st.rerun()


# =====================================================================
# UI COMPONENTS: MAIN APPLICATION AREA
# =====================================================================

# ---------------------------------------------------------
# VIEW: AUTHENTICATION PROMPT (Logged Out)
# ---------------------------------------------------------
if not st.session_state.logged_in:
    
    st.markdown(
        '<span class="header-eyebrow">Welcome to EnterpriseAssist</span>', 
        unsafe_allow_html=True
    )
    
    st.markdown(
        '<h1 class="page-title">EnterpriseAssist AI</h1>', 
        unsafe_allow_html=True
    )
    
    st.markdown(
        '<p class="page-subtitle">Your intelligent enterprise concierge</p>', 
        unsafe_allow_html=True
    )
    
    st.markdown(
        '<div class="page-divider"></div>', 
        unsafe_allow_html=True
    )
    
    st.markdown(
        f'<p style="color:{theme_manager.text_secondary}; font-size:1rem; line-height:1.6; font-family:{theme_manager.font_family_base};">'
        'Sign in using your employee credentials to access AI-powered assistance '
        'for HR, IT, Finance, Travel, and policy support.'
        '</p>',
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# VIEW: PRIMARY CHAT INTERFACE (Logged In)
# ---------------------------------------------------------
else:
    
    st.markdown(
        '<span class="header-eyebrow">AI Concierge · HR · IT · Finance · Travel</span>', 
        unsafe_allow_html=True
    )
    
    st.markdown(
        '<h1 class="page-title">EnterpriseAssist AI</h1>', 
        unsafe_allow_html=True
    )
    
    st.markdown(
        '<p class="page-subtitle">Your integrated enterprise assistant</p>', 
        unsafe_allow_html=True
    )
    
    st.markdown(
        '<div class="page-divider"></div>', 
        unsafe_allow_html=True
    )

    # Instantiate the scrollable container for the chat log
    chat_box = st.container(height=420, key="chat_scroll")
    
    with chat_box:
        
        # Iterate over historical messages and render them
        for msg in st.session_state.chat_history:
            role = msg.get("role")
            text = msg.get("text")
            
            # Determine rendering classes based on role
            avatar_text = "U" if role == "user" else "AI"
            css_class = "user" if role == "user" else "assistant"

            # Construct the chat message HTML payload
            message_html = f"""
<div class="chat-message">
    <div class="chat-avatar {css_class}">{avatar_text}</div>
    <div class="chat-bubble {css_class}">{text}</div>
</div>
"""
            st.markdown(message_html, unsafe_allow_html=True)

    # Primary Input mechanism
    user_input = st.chat_input(
        placeholder="Ask a question or request an action...", 
        key="chat_input"
    )

    # Process the user submission
    if user_input:
        
        # 1. Append the user message to local state for immediate rendering
        st.session_state.chat_history.append({
            "role": "user", 
            "text": user_input
        })

        # 2. Trigger the AI Backend Generation Cycle
        with st.spinner("Thinking..."):
            try:
                ai_reply, st.session_state.pending_action = get_ai_response(
                    st.session_state.genai_history,
                    user_input,
                    st.session_state.employee_id,
                    st.session_state.pending_action,
                )
            except Exception as e:
                # Graceful degradation if AI core fails
                ai_reply = f"Error communicating with AI Core: {str(e)}"

        # 3. Append the AI response to local state
        st.session_state.chat_history.append({
            "role": "assistant", 
            "text": ai_reply
        })
        
        # 4. Force a UI refresh to display the new cycle
        st.rerun()