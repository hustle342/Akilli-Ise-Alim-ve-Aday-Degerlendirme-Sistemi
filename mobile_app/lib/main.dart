/// Akilli Ise Alim — Flutter Uygulama Giris Noktasi
/// ===================================================
/// Multi-platform: Web, Windows, Android
/// Splash Screen -> Auth -> Rol tabanli Dashboard

import 'package:flutter/material.dart';

import 'src/ui/theme.dart';
import 'src/ui/splash_screen.dart';
import 'src/ui/app_shell.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const RecruitmentAppRoot());
}

class RecruitmentAppRoot extends StatefulWidget {
  const RecruitmentAppRoot({super.key});

  @override
  State<RecruitmentAppRoot> createState() => _RecruitmentAppRootState();
}

class _RecruitmentAppRootState extends State<RecruitmentAppRoot> {
  bool _showSplash = true;

  void _onSplashFinished() {
    setState(() {
      _showSplash = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Akilli Ise Alim',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: _showSplash
          ? SplashScreen(onFinished: _onSplashFinished)
          : const RecruitmentApp(),
    );
  }
}
