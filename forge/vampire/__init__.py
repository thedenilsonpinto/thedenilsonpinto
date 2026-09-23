"""The Midnight AI Lab forge — generates every SVG used by the black + violet vampire AI-engineer README.

GitHub renders README images through <img>. Inside such an SVG:
  * no JavaScript and no external requests (fonts/images must be inlined),
  * CSS @keyframes and SMIL animations DO run,
  * there are no pointer events (so no :hover).
Everything here is built around those rules.
"""
