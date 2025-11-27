
CREATE TABLE classes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE classes ENABLE ROW LEVEL SECURITY;

-- Policy for SELECT: Users can only view their own classes.
CREATE POLICY "Users can view own classes" ON classes
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own classes" ON classes
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own classes" ON classes
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own classes" ON classes
    FOR DELETE USING (auth.uid() = user_id);