
📄 Product Requirements Document: InboxCast

1. Product Overview

Name: InboxCast
Summary: InboxCast converts daily email newsletters into grouped, human-voiced podcast episodes. Users connect their Gmail, label the newsletters they care about, and receive summarized audio episodes to listen to on the go (e.g., during commutes or workouts).

⸻

2. Goals & Objectives
	•	Primary Goal: Help users consume written newsletter content hands-free by summarizing and voicing it into daily podcast episodes.
	•	Secondary Goals:
	•	Allow users to group newsletters by topic or source.
	•	Offer adjustable summary depth and audio style.
	•	Provide seamless podcast-style playback.
	•	Enable monetization via usage limits and premium features.

⸻

3. Core Features

3.1. Gmail Integration
	•	Authenticate users with Gmail via OAuth.
	•	Allow users to specify a Gmail label (e.g., “InboxCast-Newsletters”).
	•	Periodically fetch recent emails from the specified label.
	•	Filter for newsletter-type emails using:
	•	Metadata (unsubscribe links, known senders, email layout)
	•	User-defined inclusion rules

3.2. Topic Grouping
	•	Use LLM or keyword-based clustering to group emails by shared topics (e.g., Tech, Finance).
	•	Each topic group generates one podcast episode.
	•	Enable user override/editing of grouped topics (future enhancement).

3.3. Content Summarization
	•	Extract readable content from HTML emails (strip nav, ads, boilerplate).
	•	Summarize grouped content using adjustable settings:
	•	Summary depth (headline-only, short-form, long-form)
	•	Max episode length (e.g., 3 min, 10 min, 20 min)

3.4. Human-like Audio Generation
	•	Convert summary into audio using ElevenLabs or similar realistic TTS.
	•	Stitch multiple newsletter summaries into one podcast-style MP3.
	•	Add optional intro/outro voice snippets per episode.
	•	Generate and serve an RSS podcast feed per user for use in apps like Apple Podcasts or Spotify.

3.5. Web App Dashboard
	•	User authentication and onboarding
	•	Gmail label selection UI
	•	Summary/audio settings UI
	•	Display processed episodes with:
	•	Topic name
	•	Newsletter sources included
	•	Play/download/share buttons

⸻

4. Monetization & Access Control

Free Tier
	•	Limit: Process up to 2 grouped episodes per day
	•	Ads/sponsored content included in summary/audio

Premium Tier
	•	Unlimited newsletter-to-podcast processing
	•	LLM-based sponsor content filtering
	•	Early access to RSS/RSS-based inputs
	•	Custom voice tone and more voices

⸻

5. Technical Architecture

Layer	Stack
Frontend	React (Next.js), Tailwind CSS
Backend	FastAPI (Python), Gmail API
Database	Supabase (Postgres + Auth) or Firebase
TTS	ElevenLabs API (or PlayHT)
LLM	OpenAI GPT-4 API (summarization + grouping)
Hosting	Vercel (frontend), Render/Fly.io (backend)
Podcast Feed	RSS XML file hosted per user


⸻

6. Success Metrics

Metric	Goal
Daily active users (DAU)	1K+ by 3 months post-launch
Avg. listen-through rate	>70%
% of users upgrading to paid tier	>5%
Episode generation error rate	<3%


⸻

7. Future Roadmap

Timeline	Feature
Month 2–3	RSS feed ingestion + grouping
Month 4	Mobile app frontend (Flutter or React Native)
Month 5	Daily “auto-play” mode with background generation
Month 6+	Voice cloning or celebrity-style voices (premium upsell)
