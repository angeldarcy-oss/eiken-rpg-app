-- ============================================================
-- 英検RPG: Supabase テーブル定義
-- SupabaseダッシュボードのSQL Editorに貼り付けて一度実行する
-- ============================================================

-- アカウント
create table if not exists users (
  id             uuid primary key default gen_random_uuid(),
  username       text not null,
  username_lower text generated always as (lower(username)) stored,
  password_hash  text not null,
  created_at     timestamptz not null default now(),
  unique (username_lower)
);

-- プレイヤーデータ本体（1ユーザー1行、player dictを丸ごとJSONBで保持）
create table if not exists players (
  user_id    uuid primary key references users(id) on delete cascade,
  data       jsonb not null default '{}',
  weak_words jsonb not null default '[]',
  last_saved timestamptz not null default now()
);

-- 学習履歴（1セッション1行、追記専用）
create table if not exists history (
  id           bigint generated always as identity primary key,
  user_id      uuid not null references users(id) on delete cascade,
  played_on    date not null,
  played_at    timestamptz not null default now(),
  grade        text not null default '',
  total        int not null default 0,
  correct      int not null default 0,
  accuracy     real not null default 0,
  exp_gained   int not null default 0,
  damage_taken int not null default 0
);

create index if not exists idx_history_user on history (user_id, played_at desc);

-- 週間ランキング（1ユーザー1行）
create table if not exists rankings (
  user_id        uuid primary key references users(id) on delete cascade,
  username       text not null,
  name           text not null default '',
  character      text not null default '',
  level          int not null default 1,
  total_exp      int not null default 0,
  grade_target   text not null default 'grade_5',
  weekly_correct int not null default 0,
  weekly_total   int not null default 0,
  max_streak     int not null default 0,
  best_streak    int not null default 0,
  boss_defeats   int not null default 0,
  active_title   text,
  titles         jsonb not null default '[]',
  week_start     date not null,
  updated_at     timestamptz not null default now()
);

-- サーバー側のservice_roleキーでアクセスするためRLSは使わない。
-- 万一anonキーでのアクセスを完全に遮断したい場合は以下を有効化する:
-- alter table users    enable row level security;
-- alter table players  enable row level security;
-- alter table history  enable row level security;
-- alter table rankings enable row level security;
