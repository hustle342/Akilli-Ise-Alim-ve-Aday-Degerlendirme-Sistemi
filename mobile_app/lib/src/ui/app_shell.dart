import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';

import '../models/session_state.dart';
import '../services/api_service.dart';

class RecruitmentApp extends StatefulWidget {
  const RecruitmentApp({super.key});

  @override
  State<RecruitmentApp> createState() => _RecruitmentAppState();
}

class _RecruitmentAppState extends State<RecruitmentApp> {
  final ApiService _apiService = ApiService();
  SessionState? _session;

  void _handleLogin(SessionState session) {
    setState(() {
      _session = session;
    });
  }

  void _handleLogout() {
    setState(() {
      _session = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Akilli Ise Alim',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF0E5A8A),
          brightness: Brightness.light,
        ),
        scaffoldBackgroundColor: const Color(0xFFF4F1E8),
        useMaterial3: true,
        cardTheme: const CardThemeData(
          elevation: 0,
          margin: EdgeInsets.zero,
          color: Colors.white,
        ),
      ),
      home: _session == null
          ? AuthScreen(apiService: _apiService, onLogin: _handleLogin)
          : DashboardScreen(
              apiService: _apiService,
              session: _session!,
              onLogout: _handleLogout,
            ),
    );
  }
}

class AuthScreen extends StatefulWidget {
  const AuthScreen({
    required this.apiService,
    required this.onLogin,
    super.key,
  });

  final ApiService apiService;
  final ValueChanged<SessionState> onLogin;

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final _fullNameController = TextEditingController();
  final _emailController = TextEditingController(text: 'admin@example.com');
  final _passwordController = TextEditingController(text: 'AdminPass123!');
  final _baseUrlController = TextEditingController(
    text: 'http://127.0.0.1:8000',
  );
  final _bootstrapCodeController = TextEditingController(
    text: 'dev-bootstrap-code',
  );

  bool _isRegisterMode = false;
  bool _loading = false;
  String _role = 'candidate';
  String? _message;

  @override
  void dispose() {
    _fullNameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _baseUrlController.dispose();
    _bootstrapCodeController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() {
      _loading = true;
      _message = null;
    });

    try {
      if (_isRegisterMode) {
        await widget.apiService.register(
          baseUrl: _baseUrlController.text,
          fullName: _fullNameController.text,
          email: _emailController.text,
          password: _passwordController.text,
          role: _role,
          bootstrapCode: _bootstrapCodeController.text,
        );
        setState(() {
          _message = 'Kayit basarili. Simdi giris yapabilirsin.';
          _isRegisterMode = false;
        });
      } else {
        final session = await widget.apiService.login(
          baseUrl: _baseUrlController.text,
          email: _emailController.text,
          password: _passwordController.text,
        );
        widget.onLogin(session);
      }
    } on ApiException catch (error) {
      setState(() {
        _message = error.message;
      });
    } catch (_) {
      setState(() {
        _message = 'Beklenmeyen bir hata olustu.';
      });
    } finally {
      if (mounted) {
        setState(() {
          _loading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final titleStyle = Theme.of(context).textTheme.headlineMedium?.copyWith(
      fontWeight: FontWeight.w700,
      color: const Color(0xFF102A43),
    );

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFFE6EEF3), Color(0xFFF6E6C5)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 520),
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Card(
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(28),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Akilli Ise Alim', style: titleStyle),
                      const SizedBox(height: 8),
                      Text(
                        _isRegisterMode
                            ? 'Yeni kullanici olustur ve ardindan giris yap.'
                            : 'Backend API ile giris yapip raporlari goruntule.',
                      ),
                      const SizedBox(height: 24),
                      _buildField(_baseUrlController, 'Backend URL'),
                      if (_isRegisterMode) ...[
                        const SizedBox(height: 12),
                        _buildField(_fullNameController, 'Ad Soyad'),
                      ],
                      const SizedBox(height: 12),
                      _buildField(_emailController, 'E-posta'),
                      const SizedBox(height: 12),
                      _buildField(
                        _passwordController,
                        'Sifre',
                        obscureText: true,
                      ),
                      if (_isRegisterMode) ...[
                        const SizedBox(height: 12),
                        DropdownButtonFormField<String>(
                          initialValue: _role,
                          decoration: const InputDecoration(labelText: 'Rol'),
                          items: const [
                            DropdownMenuItem(
                              value: 'candidate',
                              child: Text('Candidate'),
                            ),
                            DropdownMenuItem(value: 'hr', child: Text('HR')),
                            DropdownMenuItem(
                              value: 'admin',
                              child: Text('Admin'),
                            ),
                          ],
                          onChanged: (value) {
                            if (value == null) return;
                            setState(() {
                              _role = value;
                            });
                          },
                        ),
                        if (_role == 'hr' || _role == 'admin') ...[
                          const SizedBox(height: 12),
                          _buildField(
                            _bootstrapCodeController,
                            'Bootstrap Code',
                          ),
                        ],
                      ],
                      if (_message != null) ...[
                        const SizedBox(height: 16),
                        Text(
                          _message!,
                          style: TextStyle(
                            color: _message!.toLowerCase().contains('basarili')
                                ? const Color(0xFF166534)
                                : const Color(0xFF991B1B),
                          ),
                        ),
                      ],
                      const SizedBox(height: 20),
                      Row(
                        children: [
                          Expanded(
                            child: FilledButton(
                              onPressed: _loading ? null : _submit,
                              child: Text(
                                _loading
                                    ? 'Bekleniyor...'
                                    : _isRegisterMode
                                    ? 'Kayit Ol'
                                    : 'Giris Yap',
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      TextButton(
                        onPressed: _loading
                            ? null
                            : () {
                                setState(() {
                                  _isRegisterMode = !_isRegisterMode;
                                  _message = null;
                                });
                              },
                        child: Text(
                          _isRegisterMode
                              ? 'Zaten hesabin var mi? Giris yap'
                              : 'Hesabin yok mu? Kayit ol',
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildField(
    TextEditingController controller,
    String label, {
    bool obscureText = false,
  }) {
    return TextField(
      controller: controller,
      obscureText: obscureText,
      decoration: InputDecoration(
        labelText: label,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(18)),
      ),
    );
  }
}

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({
    required this.apiService,
    required this.session,
    required this.onLogout,
    super.key,
  });

  final ApiService apiService;
  final SessionState session;
  final VoidCallback onLogout;

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Map<String, dynamic>? _overview;
  Map<String, dynamic>? _auditLogs;
  Map<String, dynamic>? _myApplications;
  Map<String, dynamic>? _jobs;
  Map<String, dynamic>? _jobCandidates;
  Map<String, dynamic>? _shortlisted;
  Map<String, dynamic>? _invitations;
  final _jobTitleController = TextEditingController();
  final _jobDescriptionController = TextEditingController();
  final _jobSkillsController = TextEditingController();
  String? _error;
  String? _hrMessage;
  String? _uploadMessage;
  bool _loading = true;
  bool _jobSubmitting = false;
  bool _uploading = false;
  int? _selectedJobId;
  PlatformFile? _selectedFile;

  @override
  void dispose() {
    _jobTitleController.dispose();
    _jobDescriptionController.dispose();
    _jobSkillsController.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      if (widget.session.isPrivileged) {
        final jobs = await widget.apiService.fetchJobs(widget.session);
        final overview = await widget.apiService.fetchOverview(widget.session);
        Map<String, dynamic>? auditLogs;
        Map<String, dynamic>? jobCandidates;
        final jobItems = (jobs['jobs'] as List<dynamic>? ?? const []);
        final resolvedJobId =
            _selectedJobId ??
            (jobItems.isNotEmpty
                ? (jobItems.first as Map<String, dynamic>)['id'] as int?
                : null);
        Map<String, dynamic>? shortlisted;
        Map<String, dynamic>? invitations;
        if (resolvedJobId != null) {
          jobCandidates = await widget.apiService.fetchJobCandidates(
            session: widget.session,
            jobPostingId: resolvedJobId,
          );
          shortlisted = await widget.apiService.fetchShortlisted(
            session: widget.session,
            jobPostingId: resolvedJobId,
          );
          invitations = await widget.apiService.fetchInvitations(
            session: widget.session,
            jobPostingId: resolvedJobId,
          );
        }
        if (widget.session.role == 'admin') {
          auditLogs = await widget.apiService.fetchAuditLogs(widget.session);
        }
        setState(() {
          _jobs = jobs;
          _overview = overview;
          _jobCandidates = jobCandidates;
          _shortlisted = shortlisted;
          _invitations = invitations;
          _auditLogs = auditLogs;
          _selectedJobId = resolvedJobId;
        });
      } else {
        final jobs = await widget.apiService.fetchJobs(widget.session);
        final myApplications = await widget.apiService.fetchMyApplications(
          widget.session,
        );
        setState(() {
          _jobs = jobs;
          _myApplications = myApplications;
          final jobItems = (jobs['jobs'] as List<dynamic>? ?? const []);
          if (jobItems.isNotEmpty && _selectedJobId == null) {
            _selectedJobId =
                (jobItems.first as Map<String, dynamic>)['id'] as int?;
          }
        });
      }
    } on ApiException catch (error) {
      setState(() {
        _error = error.message;
      });
    } finally {
      if (mounted) {
        setState(() {
          _loading = false;
        });
      }
    }
  }

  Future<void> _createJob() async {
    final title = _jobTitleController.text.trim();
    final description = _jobDescriptionController.text.trim();
    final minExperience = int.tryParse(
      _jobSkillsController.text.trim().split('|').first.trim(),
    );
    final rawSkills = _jobSkillsController.text.contains('|')
        ? _jobSkillsController.text.split('|').last
        : _jobSkillsController.text;
    final skills = rawSkills
        .split(',')
        .map((item) => item.trim())
        .where((item) => item.isNotEmpty)
        .toList();

    if (title.length < 2 ||
        minExperience == null ||
        minExperience < 0 ||
        skills.isEmpty) {
      setState(() {
        _hrMessage =
            'Ilan olusturmak icin baslik, deneyim ve en az bir yetenek girilmelidir. Format: 2 | flutter,dart';
      });
      return;
    }

    setState(() {
      _jobSubmitting = true;
      _hrMessage = null;
    });

    try {
      final result = await widget.apiService.createJob(
        session: widget.session,
        title: title,
        description: description,
        minYearsExperience: minExperience,
        requiredSkills: skills,
      );

      setState(() {
        _hrMessage = 'Ilan olusturuldu: ${result['title'] ?? title}';
        _jobTitleController.clear();
        _jobDescriptionController.clear();
        _jobSkillsController.clear();
      });
      await _loadData();
    } on ApiException catch (error) {
      setState(() {
        _hrMessage = error.message;
      });
    } finally {
      if (mounted) {
        setState(() {
          _jobSubmitting = false;
        });
      }
    }
  }

  Future<void> _selectHrJob(int? jobId) async {
    setState(() {
      _selectedJobId = jobId;
    });
    await _loadData();
  }

  Future<void> _pickPdf() async {
    final result = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: const ['pdf'],
      withData: true,
    );

    if (result == null || result.files.isEmpty) {
      return;
    }

    setState(() {
      _selectedFile = result.files.first;
      _uploadMessage = null;
    });
  }

  Future<void> _uploadCv() async {
    if (_selectedJobId == null ||
        _selectedFile == null ||
        _selectedFile!.bytes == null) {
      setState(() {
        _uploadMessage = 'Ilan ve PDF dosyasi secmelisin.';
      });
      return;
    }

    setState(() {
      _uploading = true;
      _uploadMessage = null;
    });

    try {
      final result = await widget.apiService.uploadApplicationCv(
        session: widget.session,
        jobPostingId: _selectedJobId!,
        fileName: _selectedFile!.name,
        fileBytes: _selectedFile!.bytes!,
      );

      setState(() {
        _uploadMessage =
            'Basvuru alindi. Skor: ${result['match_score'] ?? '-'} | Davet: ${result['invitation_created'] == true ? 'Olustu' : 'Yok'}';
        _selectedFile = null;
      });

      await _loadData();
    } on ApiException catch (error) {
      setState(() {
        _uploadMessage = error.message;
      });
    } finally {
      if (mounted) {
        setState(() {
          _uploading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Operasyon Panosu'),
        actions: [
          IconButton(onPressed: _loadData, icon: const Icon(Icons.refresh)),
          IconButton(
            onPressed: widget.onLogout,
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
          ? Center(child: Text(_error!))
          : ListView(
              padding: const EdgeInsets.all(20),
              children: [
                _IdentityCard(session: widget.session),
                const SizedBox(height: 16),
                if (widget.session.isPrivileged && _overview != null)
                  _OverviewSection(data: _overview!),
                if (widget.session.isPrivileged) ...[
                  const SizedBox(height: 16),
                  _HrManagementSection(
                    jobs: _jobs,
                    jobCandidates: _jobCandidates,
                    shortlisted: _shortlisted,
                    invitations: _invitations,
                    selectedJobId: _selectedJobId,
                    titleController: _jobTitleController,
                    descriptionController: _jobDescriptionController,
                    skillsController: _jobSkillsController,
                    message: _hrMessage,
                    jobSubmitting: _jobSubmitting,
                    onCreateJob: _createJob,
                    onSelectJob: _selectHrJob,
                  ),
                ],
                if (!widget.session.isPrivileged)
                  _CandidateApplicationsSection(
                    data: _myApplications,
                    jobs: _jobs,
                    selectedJobId: _selectedJobId,
                    selectedFileName: _selectedFile?.name,
                    uploadMessage: _uploadMessage,
                    uploading: _uploading,
                    onSelectJob: (jobId) {
                      setState(() {
                        _selectedJobId = jobId;
                      });
                    },
                    onPickPdf: _pickPdf,
                    onUpload: _uploadCv,
                  ),
                if (widget.session.role == 'admin' && _auditLogs != null) ...[
                  const SizedBox(height: 16),
                  _AuditSection(data: _auditLogs!),
                ],
              ],
            ),
    );
  }
}

class _IdentityCard extends StatelessWidget {
  const _IdentityCard({required this.session});

  final SessionState session;

  @override
  Widget build(BuildContext context) {
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Oturum Bilgisi',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Text('E-posta: ${session.email}'),
            Text('Rol: ${session.role}'),
            Text('Backend: ${session.baseUrl}'),
          ],
        ),
      ),
    );
  }
}

class _OverviewSection extends StatelessWidget {
  const _OverviewSection({required this.data});

  final Map<String, dynamic> data;

  @override
  Widget build(BuildContext context) {
    final cards = <MapEntry<String, String>>[
      MapEntry('Toplam Ilan', '${data['total_jobs'] ?? 0}'),
      MapEntry('Toplam Aday', '${data['total_candidates'] ?? 0}'),
      MapEntry('Toplam Basvuru', '${data['total_applications'] ?? 0}'),
      MapEntry('Toplam Davet', '${data['total_invitations'] ?? 0}'),
      MapEntry('Ortalama Skor', '${data['avg_score_all'] ?? 0}'),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Yonetim Ozeti', style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 12),
        Wrap(
          spacing: 12,
          runSpacing: 12,
          children: cards
              .map(
                (entry) => SizedBox(
                  width: 180,
                  child: Card(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(24),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(18),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(entry.key),
                          const SizedBox(height: 10),
                          Text(
                            entry.value,
                            style: Theme.of(context).textTheme.headlineSmall
                                ?.copyWith(fontWeight: FontWeight.bold),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              )
              .toList(),
        ),
      ],
    );
  }
}

class _AuditSection extends StatelessWidget {
  const _AuditSection({required this.data});

  final Map<String, dynamic> data;

  @override
  Widget build(BuildContext context) {
    final logs = (data['logs'] as List<dynamic>? ?? const []);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Son Audit Kayitlari',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 12),
        Card(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(24),
          ),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: logs.take(5).map((log) {
                final item = log as Map<String, dynamic>;
                return ListTile(
                  contentPadding: EdgeInsets.zero,
                  title: Text('${item['method']} ${item['path']}'),
                  subtitle: Text(
                    '${item['role']} - status ${item['status_code']}',
                  ),
                  trailing: Text('${item['ip_address']}'),
                );
              }).toList(),
            ),
          ),
        ),
      ],
    );
  }
}

class _HrManagementSection extends StatelessWidget {
  const _HrManagementSection({
    required this.jobs,
    required this.jobCandidates,
    required this.shortlisted,
    required this.invitations,
    required this.selectedJobId,
    required this.titleController,
    required this.descriptionController,
    required this.skillsController,
    required this.message,
    required this.jobSubmitting,
    required this.onCreateJob,
    required this.onSelectJob,
  });

  final Map<String, dynamic>? jobs;
  final Map<String, dynamic>? jobCandidates;
  final Map<String, dynamic>? shortlisted;
  final Map<String, dynamic>? invitations;
  final int? selectedJobId;
  final TextEditingController titleController;
  final TextEditingController descriptionController;
  final TextEditingController skillsController;
  final String? message;
  final bool jobSubmitting;
  final VoidCallback onCreateJob;
  final ValueChanged<int?> onSelectJob;

  @override
  Widget build(BuildContext context) {
    final jobItems = (jobs?['jobs'] as List<dynamic>? ?? const []);
    final candidates =
        (jobCandidates?['candidates'] as List<dynamic>? ?? const []);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Card(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(24),
          ),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Ilan Yonetimi',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: titleController,
                  decoration: const InputDecoration(labelText: 'Ilan Basligi'),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: descriptionController,
                  maxLines: 3,
                  decoration: const InputDecoration(labelText: 'Aciklama'),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: skillsController,
                  decoration: const InputDecoration(
                    labelText: 'Deneyim | Yetenekler',
                    hintText: '2 | flutter,dart,git',
                  ),
                ),
                if (message != null) ...[
                  const SizedBox(height: 12),
                  Text(message!),
                ],
                const SizedBox(height: 12),
                FilledButton(
                  onPressed: jobSubmitting ? null : onCreateJob,
                  child: Text(
                    jobSubmitting ? 'Olusturuluyor...' : 'Ilan Olustur',
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        Card(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(24),
          ),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Aday Siralamasi',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<int>(
                  initialValue: selectedJobId,
                  decoration: const InputDecoration(labelText: 'Ilan Sec'),
                  items: jobItems
                      .map(
                        (item) => DropdownMenuItem<int>(
                          value: (item as Map<String, dynamic>)['id'] as int?,
                          child: Text(item['title']?.toString() ?? 'Ilan'),
                        ),
                      )
                      .toList(),
                  onChanged: jobItems.isEmpty ? null : onSelectJob,
                ),
                const SizedBox(height: 12),
                if (candidates.isEmpty)
                  const Text('Secili ilan icin henuz aday bulunmuyor.')
                else
                  ...candidates.take(5).map((item) {
                    final candidateRow = item as Map<String, dynamic>;
                    final candidate =
                        candidateRow['candidate'] as Map<String, dynamic>? ??
                        const {};
                    return ListTile(
                      contentPadding: EdgeInsets.zero,
                      title: Text(candidate['full_name']?.toString() ?? 'Aday'),
                      subtitle: Text(candidate['email']?.toString() ?? ''),
                      trailing: Text('${candidateRow['match_score'] ?? '-'}'),
                    );
                  }),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        _ShortlistCard(shortlisted: shortlisted, invitations: invitations),
      ],
    );
  }
}

class _ShortlistCard extends StatelessWidget {
  const _ShortlistCard({
    required this.shortlisted,
    required this.invitations,
  });

  final Map<String, dynamic>? shortlisted;
  final Map<String, dynamic>? invitations;

  @override
  Widget build(BuildContext context) {
    final shortItems =
        (shortlisted?['candidates'] as List<dynamic>? ?? const []);
    final inviteItems =
        (invitations?['invitations'] as List<dynamic>? ?? const []);

    // Build a lookup: application_id -> invitation info
    final inviteByAppId = <int, Map<String, dynamic>>{};
    for (final inv in inviteItems) {
      final item = inv as Map<String, dynamic>;
      final appId = item['application_id'] as int?;
      if (appId != null) inviteByAppId[appId] = item;
    }

    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.star_rounded, color: Color(0xFF0E5A8A)),
                const SizedBox(width: 8),
                Text(
                  'Kisa Liste (Baraj ≥ 70)',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ],
            ),
            const SizedBox(height: 12),
            if (shortItems.isEmpty)
              const Text('Bu ilan icin kisa listeye giren aday bulunmuyor.')
            else
              ...shortItems.map((item) {
                final row = item as Map<String, dynamic>;
                final name = row['candidate_name']?.toString() ?? 'Aday';
                final score = row['score'];
                final appId = row['application_id'] as int?;
                final invite = appId != null ? inviteByAppId[appId] : null;

                final inviteLabel = invite != null
                    ? '${invite['type'] ?? ''} · ${invite['status'] ?? ''}'
                    : 'Davet yok';

                final inviteColor = () {
                  final status = invite?['status']?.toString() ?? '';
                  if (status == 'sent') return Colors.green;
                  if (status == 'completed') return Colors.blue;
                  if (status == 'canceled') return Colors.red;
                  return Colors.grey;
                }();

                return Card(
                  margin: const EdgeInsets.only(bottom: 8),
                  color: const Color(0xFFF4F8FB),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: ListTile(
                    leading: CircleAvatar(
                      backgroundColor: const Color(0xFF0E5A8A),
                      child: Text(
                        name.substring(0, 1).toUpperCase(),
                        style: const TextStyle(color: Colors.white),
                      ),
                    ),
                    title: Text(name),
                    subtitle: Text('Basvuru #${appId ?? '-'}'),
                    trailing: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Text(
                          'Skor: $score',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        Text(
                          inviteLabel,
                          style: TextStyle(fontSize: 11, color: inviteColor),
                        ),
                      ],
                    ),
                  ),
                );
              }),
          ],
        ),
      ),
    );
  }
}

class _CandidateApplicationsSection extends StatelessWidget {
  const _CandidateApplicationsSection({
    required this.data,
    required this.jobs,
    required this.selectedJobId,
    required this.selectedFileName,
    required this.uploadMessage,
    required this.uploading,
    required this.onSelectJob,
    required this.onPickPdf,
    required this.onUpload,
  });

  final Map<String, dynamic>? data;
  final Map<String, dynamic>? jobs;
  final int? selectedJobId;
  final String? selectedFileName;
  final String? uploadMessage;
  final bool uploading;
  final ValueChanged<int?> onSelectJob;
  final VoidCallback onPickPdf;
  final VoidCallback onUpload;

  @override
  Widget build(BuildContext context) {
    final applications = (data?['applications'] as List<dynamic>? ?? const []);
    final jobItems = (jobs?['jobs'] as List<dynamic>? ?? const []);

    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Basvurularim', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            DropdownButtonFormField<int>(
              initialValue: selectedJobId,
              decoration: const InputDecoration(labelText: 'Ilan Sec'),
              items: jobItems
                  .map(
                    (item) => DropdownMenuItem<int>(
                      value: (item as Map<String, dynamic>)['id'] as int?,
                      child: Text(item['title']?.toString() ?? 'Ilan'),
                    ),
                  )
                  .toList(),
              onChanged: jobItems.isEmpty ? null : onSelectJob,
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: onPickPdf,
                    icon: const Icon(Icons.picture_as_pdf_outlined),
                    label: Text(selectedFileName ?? 'PDF Sec'),
                  ),
                ),
                const SizedBox(width: 12),
                FilledButton(
                  onPressed: uploading ? null : onUpload,
                  child: Text(uploading ? 'Yukleniyor...' : 'CV Yukle'),
                ),
              ],
            ),
            if (uploadMessage != null) ...[
              const SizedBox(height: 12),
              Text(uploadMessage!),
            ],
            const SizedBox(height: 16),
            if (applications.isEmpty)
              const Text(
                'Henuz kayitli basvuru yok. Ustten bir ilan secip PDF CV yukleyebilirsin.',
              )
            else
              ...applications.map((item) {
                final application = item as Map<String, dynamic>;
                final invitation =
                    application['invitation'] as Map<String, dynamic>?;
                return Padding(
                  padding: const EdgeInsets.only(top: 12),
                  child: Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF8FAFC),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${application['job_title'] ?? 'Ilan'}',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        const SizedBox(height: 8),
                        Text('Durum: ${application['status'] ?? '-'}'),
                        Text('Skor: ${application['match_score'] ?? '-'}'),
                        Text(
                          'Davet: ${invitation == null ? 'Yok' : invitation['status'] ?? '-'}',
                        ),
                        const SizedBox(height: 8),
                        Text(
                          '${application['parsed_summary'] ?? ''}',
                          maxLines: 3,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                );
              }),
          ],
        ),
      ),
    );
  }
}
