import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Hadith App',
      // ضبط اتجاه النص ليصبح من اليمين إلى اليسار للغة العربية
      builder: (context, child) {
        return Directionality(
          textDirection: TextDirection.rtl,
          child: child!,
        );
      },
      theme: ThemeData(
        primarySwatch: Colors.green,
        scaffoldBackgroundColor: const Color(0xFFA78295),
      ),
      home: const HadithDetailReaderScreen(),
    );
  }
}

class HadithDetailReaderScreen extends StatefulWidget {
  const HadithDetailReaderScreen({super.key});

  @override
  State<HadithDetailReaderScreen> createState() => _HadithDetailReaderScreenState();
}

class _HadithDetailReaderScreenState extends State<HadithDetailReaderScreen> {
  final List<String> hadiths = [
    'إنما الأعمال بالنيات وإنما لكل امرئ ما نوى.',
    'الدين النصيحة.',
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('تفاصيل الحديث'),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(12.0),
        child: ListView.builder(
          itemCount: hadiths.length,
          itemBuilder: (context, index) => Container(
            margin: const EdgeInsets.only(bottom: 12.0),
            padding: const EdgeInsets.all(16.0),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              hadiths[index],
              style: const TextStyle(
                fontSize: 18,
                height: 1.6,
                color: Colors.black87,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
