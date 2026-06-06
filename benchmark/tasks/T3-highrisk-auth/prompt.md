We are changing how the product authenticates API requests:

- Session access tokens must expire after 15 minutes (down from 24 hours).
- Any token missing an `aud` (audience) claim must be rejected.
- These rules apply to every authenticated endpoint.

This changes authentication and authorization behavior. Decide and record the
change the way this repository expects high-risk, security-sensitive work to be
handled, then state the resulting policy. (You do not need to implement a full
server; focus on classifying, deciding, and recording this change correctly.)
