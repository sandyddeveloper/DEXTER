"""
ASCII and Braille frames for the DEXTER Neural Orb.
Each frame is 15-20 rows high and 40-50 wide.
"""

# Simple Braille patterns for a "pulsing" orb
ORB_FRAMES = {
    "standby": [
        "       ⠠⠤⠤⠤⠄       ",
        "    ⠐⠋       ⠙⠒   ",
        "  ⠐⠁           ⠈⠂ ",
        " ⠌               ⠡ ",
        " ⠆               ⠰ ",
        " ⠇               ⠸ ",
        " ⠆               ⠰ ",
        " ⠘               ⠝ ",
        "  ⠠⠁           ⠐⠄ ",
        "    ⠑⠢       ⠔⠊   ",
        "       ⠉⠒⠒⠒⠉       "
    ],
    "listening": [
        "       ⠠⠤⠤⠤⠄       ",
        "    ⠐⠋⠒⠒⠒⠒⠒⠙⠒   ",
        "  ⠐⠁ ⠒⠒⠒⠒⠒     ⠈⠂ ",
        " ⠌  ⠒⠒⠒⠒⠒⠒⠒⠒⠒⠒ ⠡ ",
        " ⠆ ⠒⠒⠒⠒⠒⠒⠒⠒⠒⠒⠒ ⠰ ",
        " ⠇  ⠒⠒⠒⠒⠒⠒⠒⠒⠒ ⠸ ",
        " ⠆   ⠒⠒⠒⠒⠒⠒⠒   ⠰ ",
        " ⠘     ⠒⠒⠒     ⠝ ",
        "  ⠠⠁           ⠐⠄ ",
        "    ⠑⠢       ⠔⠊   ",
        "       ⠉⠒⠒⠒⠉       "
    ],
    "thinking": [
        "       ⠠⠤⠤⠤⠄       ",
        "    ⠐⠋  ⠶⠶⠶  ⠙⠒   ",
        "  ⠐⠁   ⠶⠶⠶⠶   ⠈⠂ ",
        " ⠌    ⠶⠶⠶⠶⠶    ⠡ ",
        " ⠆    ⠶⠶⠶⠶⠶    ⠰ ",
        " ⠇    ⠶⠶⠶⠶⠶    ⠸ ",
        " ⠆    ⠶⠶⠶⠶⠶    ⠰ ",
        " ⠘     ⠶⠶⠶     ⠝ ",
        "  ⠠⠁           ⠐⠄ ",
        "    ⠑⠢       ⠔⠊   ",
        "       ⠉⠒⠒⠒⠉       "
    ]
}

# Add more complex frames for smoother scaling/rotation if needed
def get_orb_frame(status: str, frame_idx: int):
    # status: STANDBY, LISTENING, THINKING
    frames = ORB_FRAMES.get(status.lower(), ORB_FRAMES["standby"])
    # We can rotate or shift them based on frame_idx
    return "\n".join(frames)
