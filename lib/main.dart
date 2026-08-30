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
      title: 'تطبيق الحديث والأذكار',
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
      home: const MainHomeScreen(),
    );
  }
}

class MainHomeScreen extends StatefulWidget {
  const MainHomeScreen({super.key});

  @override
  State<MainHomeScreen> createState() => _MainHomeScreenState();
}

class _MainHomeScreenState extends State<MainHomeScreen> {
  int _selectedIndex = 0;

  // الكتب التسعة
  final List<String> books = [
    'صحيح البخاري',
    'صحيح مسلم',
    'سنن أبي داود',
    'سنن الترمذي',
    'سنن النسائي',
    'سنن ابن ماجه',
    'موطأ مالك',
    'مسند أحمد',
    'سنن الدارمي',
  ];

  // الأذكار
  final List<String> azkar = [
    'أذكار الصباح',
    'أذكار المساء',
    'أذكار النوم',
    'أذكار الاستيقاظ',
    'أذكار الصلاة',
  ];

  // الأحاديث المختارة
  final List<String> hadiths = [
    'إنما الأعمال بالنيات وإنما لكل امرئ ما نوى.',
    'الدين النصيحة.',
    'من حسن إسلام المرء تركه ما لا يعنيه.',
    'لا يؤمن أحدكم حتى يحب لأخيه ما يحب لنفسه.',
  ];

  @override
  Widget build(BuildContext context) {
    List<String> currentList;
    String currentTitle;

    if (_selectedIndex == 0) {
      currentList = books;
      currentTitle = 'الكتب التسعة';
    } else if (_selectedIndex == 1) {
      currentList = azkar;
      currentTitle = 'الأذكار';
    } else {
      currentList = hadiths;
      currentTitle = 'الأحاديث';
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(currentTitle),
        centerTitle: true,
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(12.0),
        itemCount: currentList.length,
        itemBuilder: (context, index) => Container(
          margin: const EdgeInsets.only(bottom: 10.0),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
          ),
          child: ListTile(
            title: Text(
              currentList[index],
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            trailing: const Icon(Icons.arrow_forward_ios, size: 18),
            onTap: () {},
          ),
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) {
          setState(() {
            _selectedIndex = index;
          });
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.menu_book),
            label: 'الكتب التسعة',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.auto_awesome),
            label: 'الأذكار',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.format_quote),
            label: 'الأحاديث',
          ),
        ],
      ),
    );
  }
}
