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
      theme: ThemeData(
        primarySwatch: Colors.green,
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
  // قائمة تجريبية للأحاديث
  final List<String> hadiths = [
    'إنما الأعمال بالنيات وإنما لكل امرئ ما نوى.',
    'الدين النصيحة.',
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('تفاصيل الحديث'),
      ),
      body: ListView.builder(
        itemCount: hadiths.length,
        itemBuilder: (context, index) => Container(
          margin: const EdgeInsets.all(8.0),
          padding: const EdgeInsets.all(12.0),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            hadiths[index],
            style: const TextStyle(fontSize: 16, height: 1.8),
          ),
        ),
      ),
    );
  }
}

