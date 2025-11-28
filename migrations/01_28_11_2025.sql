CREATE TABLE cuecard_sets (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE cuecard_sets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own cuecard_sets" ON cuecard_sets
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own cuecard_sets" ON cuecard_sets
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own cuecard_sets" ON cuecard_sets
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own cuecard_sets" ON cuecard_sets
    FOR DELETE USING (auth.uid() = user_id);