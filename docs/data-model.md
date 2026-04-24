# Veri Modeli (Ilk Surum)

## Tablolar
1. users
- Aday, IK uzmanı ve admin hesaplari
- Alanlar: id, full_name, email, role, created_at

2. job_postings
- Acik pozisyon bilgileri
- Alanlar: id, title, description, min_years_experience, required_skills, created_at

3. applications
- Adayin bir ilana yaptigi basvuru
- Alanlar: id, candidate_id, job_posting_id, cv_path, parsed_summary, status, created_at

4. match_scores
- Basvuru icin uretilen uyum skoru
- Alanlar: id, application_id, score, scoring_version, rationale, created_at

5. invitations
- Test veya mulakat daveti kayitlari
- Alanlar: id, application_id, invitation_type, status, scheduled_at, created_at

## Iliskiler
- users (candidate) 1-N applications
- job_postings 1-N applications
- applications 1-N match_scores
- applications 1-N invitations

## Durum Enumlari
- ApplicationStatus: applied, shortlisted, rejected, hired
- InvitationType: test, interview
- InvitationStatus: pending, sent, completed, canceled
