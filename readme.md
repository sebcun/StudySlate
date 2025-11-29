# StudySlate

An all-in-one study platform designed to help students lock in. I made this as I have just started year 12 (australias final year of school) and want to focus on my studies more. This was also made for Siege week 9 for Hackclub.

## Features

- **Add Classes**: Create and organize your classes to keep everything tidy.
- **OneNote-Style Notes**: Create notes in a familiar interface.
- **Todo & Assignment Reminders**: Set tasks and deadlines to stay on top.
- **Cue Cards**: Create and practice with cuecard sets.
- **Focus Timer**: A winter themed focus timer.

## Installation

1. **Clone the repo**:
   ```bash
   git clone https://github.com/yourusername/studyslate.git
   cd studyslate
   ```

````
2. **Install dependencies**:
```bash
pip install -r requirements.txt
````

3. **Setup Supabase**:

- Create a Supabase project at supabase.com.
- Run the SQL migrations in the migrations/ folder in your Supabase SQL editor (in order).
  -Get your Supabase URL and anon key.

4. **Create ENV**:
   Create a .env file in the root directory:

```
SECRET_KEY=your_secret_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

5. **Run the app**:

```bash
py app.py
```

### AI Usage/Disclaimer

AI was only used for:

- Generating the SQL for any migrations with supabase. These can be found in /migrations.
- Helping out with some animations in CSS (especially todo lists)
- Creating any mock data for frontend development
- some tag lines
