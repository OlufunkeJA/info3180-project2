-- Seed script for accounts and member profiles
-- Adjust the schema/table names if your database uses a different prefix.

BEGIN;

-- Remove any existing seed accounts and linked profiles by handle/email.
DELETE FROM member_profiles WHERE acct_id IN (
  SELECT id FROM accounts WHERE handle IN ('jdoe', 'asmith', 'mjackson')
);
DELETE FROM accounts WHERE handle IN ('jdoe', 'asmith', 'mjackson') OR email_address IN ('jdoe@example.com', 'asmith@example.com', 'mjackson@example.com');

WITH new_accounts AS (
  INSERT INTO accounts (handle, email_address, pw_hash, registered_at)
  VALUES
    ('jdoe', 'jdoe@example.com', '$2b$12$KQzO7EaJXTc2GvmLFxTVweVy7tu8Hd9Q2AyMyDJBAr/cIBVMU3kKu', NOW()),
    ('asmith', 'asmith@example.com', '$2b$12$izotZj4Q8Cdi5PFv0HG8rOR6PJYDzWeg2ykxifUdU1RQM94ZforCG', NOW()),
    ('mjackson', 'mjackson@example.com', '$2b$12$GiC5OBIOx90Xregco2dJ7OFicq7J2o7gJtPdqTPnOi8bFki4bfSqq', NOW())
  RETURNING id, handle
)
INSERT INTO member_profiles (
  acct_id,
  first_name,
  surname,
  birthdate,
  gender,
  seeking,
  about_me,
  parish,
  city,
  country,
  min_age,
  max_age,
  visible,
  created_at,
  modified_at
)
SELECT
  na.id,
  v.first_name,
  v.surname,
  v.birthdate::date,
  v.gender,
  v.seeking,
  v.about_me,
  v.parish,
  v.city,
  v.country,
  v.min_age,
  v.max_age,
  v.visible,
  NOW(),
  NOW()
FROM new_accounts na
JOIN (
  VALUES
    ('jdoe', 'Jane', 'Doe', '1995-07-12', 'female', 'any', 'Love hiking, coffee, and good conversation.', 'Kingston', 'Kingston', 'Jamaica', 24, 40, TRUE),
    ('asmith', 'Alex', 'Smith', '1991-03-05', 'male', 'female', 'Software engineer who enjoys art and travel.', 'St Andrew', 'St Andrew', 'Jamaica', 23, 45, TRUE),
    ('mjackson', 'Maya', 'Jackson', '1998-11-22', 'female', 'any', 'Bookworm, foodie, and weekend beach lover.', 'Portland', 'Port Antonio', 'Jamaica', 20, 35, TRUE)
) AS v(handle, first_name, surname, birthdate, gender, seeking, about_me, parish, city, country, min_age, max_age, visible)
ON na.handle = v.handle;

COMMIT;
