import 'package02package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:intl/intl.dart';
import 'package:adhan/adhan.dart';

void main() {
  runApp(const IslamicApp());
}

class IslamicApp extends StatelessWidget {
  const IslamicApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'الرفيق الإسلامي',
      theme: ThemeData(
        fontFamily: 'sans-serif',
        scaffoldBackgroundColor: const Color(0xFFF9F6EE),
        primaryColor: const Color(0xFF287968),
      ),
      home: const MainTabScreen(),
    );
  }
}

class MainTabScreen extends StatefulWidget {
  const MainTabScreen({super.key});

  @override
  State<MainTabScreen> createState() => _MainTabScreenState();
}

class _MainTabScreenState extends State<MainTabScreen> {
  int _selectedIndex = 0;

  final List<Widget> _screens = [
    const HadithHomeScreen(),
    const AzkarCategoriesScreen(),
    const PrayerTimesScreen(),
    const SettingsAndNotificationScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        body: _screens[_selectedIndex],
        bottomNavigationBar: BottomNavigationBar(
          currentIndex: _selectedIndex,
          onTap: (index) => setState(() => _selectedIndex = index),
          selectedItemColor: const Color(0xFFB58A44),
          unselectedItemColor: Colors.grey,
          type: BottomNavigationBarType.fixed,
          backgroundColor: Colors.white,
          items: const [
            BottomNavigationBarItem(icon: Icon(Icons.menu_book_outlined), label: 'الكتب'),
            BottomNavigationBarItem(icon: Icon(Icons.auto_stories), label: 'الأذكار'),
            BottomNavigationBarItem(icon: Icon(Icons.access_time), label: 'الصلاة'),
            BottomNavigationBarItem(icon: Icon(Icons.notifications_active_outlined), label: 'التنبيهات'),
          ],
        ),
      ),
    );
  }
}

class HadithHomeScreen extends StatelessWidget {
  const HadithHomeScreen({super.key});

  final List<Map<String, String>> books = const [
    {'apiKey': 'bukhari', 'title': 'صحيح البخاري', 'calligraphy': 'صحيح\nالبخاري', 'color': '0xFF287968'},
    {'apiKey': 'muslim', 'title': 'صحيح مسلم', 'calligraphy': 'صحيح\nمسلم', 'color': '0xFF4A739C'},
    {'apiKey': 'abudawud', 'title': 'سنن أبي داود', 'calligraphy': 'سنن\nأبي داود', 'color': '0xFF566785'},
    {'apiKey': 'tirmidhi', 'title': 'جامع الترمذي', 'calligraphy': 'جامع\nالترمذي', 'color': '0xFF804B57'},
    {'apiKey': 'nasai', 'title': 'سنن النسائي', 'calligraphy': 'سنن\nالنسائي', 'color': '0xFF5E676B'},
    {'apiKey': 'ibnmajah', 'title': 'سنن ابن ماجه', 'calligraphy': 'سنن\nابن ماجه', 'color': '0xFF6B4D70'},
    {'apiKey': 'malik', 'title': 'موطأ مالك', 'calligraphy': 'موطأ\nمالك', 'color': '0xFF356953'},
    {'apiKey': 'darimi', 'title': 'سنن الدارمي', 'calligraphy': 'مسند\nالدارمي', 'color': '0xFF966242'},
    {'apiKey': 'ahmed', 'title': 'مسند أحمد', 'calligraphy': 'مسند\nأحمد', 'color': '0xFF9B3F38'},
  ];

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Text('مكتبة الحديث الشريف', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            GridView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 3, crossAxisSpacing: 12, mainAxisSpacing: 12, childAspectRatio: 0.75,
              ),
              itemCount: books.length,
              itemBuilder: (context, index) {
                final book = books[index];
                final bgColor = Color(int.parse(book['color']!));
                return GestureDetector(
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => HadithDetailReaderScreen(bookKey: book['apiKey']!, bookTitle: book['title']!, headerColor: bgColor)),
                  ),
                  child: Container(
                    decoration: BoxDecoration(color: bgColor, borderRadius: BorderRadius.circular(12)),
                    child: Center(child: Text(book['calligraphy']!, textAlign: TextAlign.center, style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold))),
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

class AzkarCategoriesScreen extends StatelessWidget {
  const AzkarCategoriesScreen({super.key});

  final Map<String, List<Map<String, dynamic>>> azkarData = const {
    'أذكار الصباح': [
      {'text': 'أَصْبَحْنَا وَأَصْبَحَ المُلْكُ لِلَّهِ، وَالْحَمْدُ لِلَّهِ...', 'count': 1},
      {'text': 'آية الكرسي: اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ...', 'count': 1},
      {'text': 'سُبْحَانَ اللهِ وَبِحَمْدِهِ', 'count': 100},
    ],
    'أذكار المساء': [
      {'text': 'أَمْسَيْنَا وَأَمْسَى المُلْكُ لِلَّهِ وَالْحَمْدُ لِلَّهِ...', 'count': 1},
      {'text': 'أَعُوذُ بِكَلِمَاتِ اللهِ التَّامَّاتِ مِنْ شَرِّ مَا خَلَقَ', 'count': 3},
    ],
    'أذكار الصلاة': [
      {'text': 'أَسْتَغْفِرُ اللَّهَ (ثَلاثاً)، اللَّهُمَّ أَنْتَ السَّلامُ وَمِنْكَ السَّلامُ...', 'count': 1},
      {'text': 'سُبْحَانَ اللَّهِ (33) ، الْحَمْدُ لِلَّهِ (33) ، اللَّهُ أَكْبَرُ (33)', 'count': 33},
    ],
    'أذكار النوم': [
      {'text': 'بِاسْمِكَ رَبِّي وَضَعْتُ جَنْبِي وَبِكَ أَرْفَعُهُ...', 'count': 1},
      {'text': 'اللَّهُمَّ قِنِي عَذَابَكَ يَوْمَ تَبْعَثُ عِبَادَكَ', 'count': 3},
    ]
  };

  @override
  Widget build(BuildContext context) {
    final categories = azkarData.keys.toList();
    return Scaffold(
      appBar: AppBar(title: const Text('الأذكار والأدعية'), backgroundColor: const Color(0xFF287968)),
      body: ListView.builder(
        padding: const EdgeInsets.all(12),
        itemCount: categories.length,
        itemBuilder: (context, index) {
          final cat = categories[index];
          return Card(
            child: ListTile(
              leading: const Icon(Icons.bookmark, color: Color(0xFFB58A44)),
              title: Text(cat, style: const TextStyle(fontWeight: FontWeight.bold)),
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              onTap: () => Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => AzkarListScreen(title: cat, items: azkarData[cat]!)),
              ),
            ),
          );
        },
      ),
    );
  }
}

class AzkarListScreen extends StatefulWidget {
  final String title;
  final List<Map<String, dynamic>> items;
  const AzkarListScreen({super.key, required this.title, required this.items});

  @override
  State<AzkarListScreen> createState() => _AzkarListScreenState();
}

class _AzkarListScreenState extends State<AzkarListScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.title), backgroundColor: const Color(0xFF287968)),
      body: ListView.builder(
        padding: const EdgeInsets.all(12),
        itemCount: widget.items.length,
        itemBuilder: (context, index) {
          final item = widget.items[index];
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  Text(item['text'], style: const TextStyle(fontSize: 16, height: 1.6), textAlign: TextAlign.center),
                  const SizedBox(height: 12),
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFB58A44)),
                    onPressed: () {
                      setState(() {
                        if (item['count'] > 0) item['count']--;
                      });
                    },
                    child: Text('التكرار المتبقي: ${item['count']}', style: const TextStyle(color: Colors.white)),
                  )
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

class PrayerTimesScreen extends StatelessWidget {
  const PrayerTimesScreen({super.key});

  Map<String, String> getPrayerTimes() {
    final coordinates = Coordinates(30.0444, 31.2357);
    final params = CalculationMethod.egyptian.getParameters();
    params.madhab = Madhab.shafi;
    final prayerTimes = PrayerTimes.today(coordinates, params);

    return {
      'الفجر': DateFormat.jm('ar').format(prayerTimes.fajr),
      'الشروق': DateFormat.jm('ar').format(prayerTimes.sunrise),
      'الظهر': DateFormat.jm('ar').format(prayerTimes.dhuhr),
      'العصر': DateFormat.jm('ar').format(prayerTimes.asr),
      'المغرب': DateFormat.jm('ar').format(prayerTimes.maghrib),
      'العشاء': DateFormat.jm('ar').format(prayerTimes.isha),
    };
  }

  @override
  Widget build(BuildContext context) {
    final times = getPrayerTimes();
    return Scaffold(
      appBar: AppBar(title: const Text('مواقيت الصلاة'), backgroundColor: const Color(0xFF287968)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: times.entries.map((e) => Card(
          child: ListTile(
            leading: const Icon(Icons.access_time_filled, color: Color(0xFF287968)),
            title: Text(e.key, style: const TextStyle(fontWeight: FontWeight.bold)),
            trailing: Text(e.value, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFFB58A44))),
          ),
        )).toList(),
      ),
    );
  }
}

class SettingsAndNotificationScreen extends StatefulWidget {
  const SettingsAndNotificationScreen({super.key});

  @override
  State<SettingsAndNotificationScreen> createState() => _SettingsAndNotificationScreenState();
}

class _SettingsAndNotificationScreenState extends State<SettingsAndNotificationScreen> {
  bool isSalawatActive = true;
  String interval = 'كل ساعة';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('التنبيهات الإيمانية'), backgroundColor: const Color(0xFF287968)),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Card(
              child: SwitchListTile(
                activeColor: const Color(0xFF287968),
                title: const Text('تنبيه الصلاة على النبي ﷺ', style: TextStyle(fontWeight: FontWeight.bold)),
                subtitle: const Text('إرسال إشعار تذكيري «اللهم صلِّ وسلم على نبينا محمد»'),
                value: isSalawatActive,
                onChanged: (val) => setState(() => isSalawatActive = val),
              ),
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF287968), padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12)),
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('«اللهم صلِّ وسلم وبارك على نبينا محمد ﷺ»'), backgroundColor: Color(0xFF287968)),
                );
              },
              icon: const Icon(Icons.notifications_active, color: Colors.white),
              label: const Text('تجربة الإشعار الآن', style: TextStyle(color: Colors.white)),
            )
          ],
        ),
      ),
    );
  }
}

class HadithDetailReaderScreen extends StatefulWidget {
  final String bookKey;
  final String bookTitle;
  final Color headerColor;
  const HadithDetailReaderScreen({super.key, required this.bookKey, required this.bookTitle, required this.headerColor});

  @override
  State<HadithDetailReaderScreen> createState() => _HadithDetailReaderScreenState();
}

class _HadithDetailReaderScreenState extends State<HadithDetailReaderScreen> {
  List<dynamic> hadiths = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchHadiths();
  }

  Future<void> fetchHadiths() async {
    try {
      final url = Uri.parse('https://hadithapi.com/api/hadiths?apiKey=\$2y\$10\$1234567890abcdefghijklmnopqrstuvwxyz&book=${widget.bookKey}&paginate=20');
      final response = await http.get(url);
      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        setState(() { hadiths = data['hadiths']['data'] ?? []; isLoading = false; });
      } else {
        loadFallback();
      }
    } catch (e) { loadFallback(); }
  }

  void loadFallback() {
    setState(() {
      isLoading = false;
      hadiths = [{'hadithNumber': '1', 'hadithArabic': 'عَنْ عُمَرَ بْنِ الْخَطَّابِ قَالَ: سَمِعْتُ رَسُولَ اللَّهِ ﷺ يَقُولُ: "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ..."'}];
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(backgroundColor: widget.headerColor, title: Text(widget.bookTitle)),
      body: isLoading
          ? Center(child: CircularProgressIndicator(color: widget.headerColor))
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: hadiths.length,
              itemBuilder: (context, index) => Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(8)),
                child: Text(hadiths[index]['hadithArabic'] ?? '', style: const TextStyle(fontSize: 16, height: 1.8)),
              ),
            ),
    );
  }
}

