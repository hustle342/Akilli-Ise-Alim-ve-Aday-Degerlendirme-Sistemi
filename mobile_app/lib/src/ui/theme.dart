/// Akilli Ise Alim — Tema Sistemi
/// ================================
/// Uygulama genelinde kullanilan renk paleti, tipografi ve
/// widget stil tanimlari.

import 'package:flutter/material.dart';

class AppTheme {
  AppTheme._();

  // ── Renk Paleti ──
  static const Color primaryDark = Color(0xFF0A2540);
  static const Color primary = Color(0xFF0E5A8A);
  static const Color primaryLight = Color(0xFF3A8CC2);
  static const Color accent = Color(0xFFF5A623);
  static const Color accentLight = Color(0xFFF6E6C5);
  static const Color background = Color(0xFFF4F1E8);
  static const Color surface = Colors.white;
  static const Color surfaceAlt = Color(0xFFF4F8FB);
  static const Color textPrimary = Color(0xFF102A43);
  static const Color textSecondary = Color(0xFF627D98);
  static const Color success = Color(0xFF166534);
  static const Color error = Color(0xFF991B1B);

  // ── Tema ──
  static ThemeData get lightTheme => ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: primary,
          brightness: Brightness.light,
        ),
        scaffoldBackgroundColor: background,
        useMaterial3: true,
        fontFamily: 'Segoe UI',
        appBarTheme: const AppBarTheme(
          backgroundColor: primaryDark,
          foregroundColor: Colors.white,
          elevation: 0,
          centerTitle: true,
        ),
        cardTheme: CardThemeData(
          elevation: 0,
          margin: EdgeInsets.zero,
          color: surface,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(24),
          ),
        ),
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(18),
            ),
          ),
        ),
        outlinedButtonTheme: OutlinedButtonThemeData(
          style: OutlinedButton.styleFrom(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(18),
            ),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(18),
          ),
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 14,
          ),
        ),
        textTheme: const TextTheme(
          headlineMedium: TextStyle(
            fontWeight: FontWeight.w700,
            color: textPrimary,
          ),
          titleLarge: TextStyle(
            fontWeight: FontWeight.w600,
            color: textPrimary,
          ),
        ),
      );

  // ── Gradient ──
  static const LinearGradient authGradient = LinearGradient(
    colors: [Color(0xFFE6EEF3), Color(0xFFF6E6C5)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient splashGradient = LinearGradient(
    colors: [primaryDark, primary],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );
}
