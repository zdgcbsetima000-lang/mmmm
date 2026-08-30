import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:convert';

void main() {
  runApp(const HadithApp());
}

class HadithApp extends StatelessWidget {
  const HadithApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'موسوعة الحديث الشريف',
      builder: (context, child) {
        return Directionality(
          textDirection: TextDirection.rtl,
          child: child!,
        );
      },
      theme: ThemeData(
        primarySwatch: Colors.teal,
        scaffoldBackgroundColor: const Color(0xFFA78295),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF3F2E56),
          foregroundColor: Colors.white,
        ),
      ),
      home: const BooksListScreen(),
    );
  }
}

class BooksListScreen extends StatelessWidget {
  const BooksListScreen({super.key});

  // قوائم الكتب التسعة المربوطة بمستودع GitHub للأحاديث
  final List<Map<String, String>> books = const [
    {'name': 'صحيح البخاري', 'key': 'ara-bukhari'},
    {'name': 'صحيح مسلم', 'key': 'ara-muslim'},
    {'name': 'سنن أبي داود', 'key': 'ara-abudawud'},
    {'name': 'سنن الترمذي', 'key': 'ara-tirmidhi'},
    {'name': 'سنن النسائي', 'key': 'ara-nasai'},
    {'name': 'سنن ابن ماجه', 'key': 'ara-ibnmajah'},
    {'name': 'موطأ مالك', 'key': 'ara-malik'},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('فهرس الكتب التسعة الشامل'),
        centerTitle: true,
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(12),
        itemCount: books.length,
        itemBuilder: (context, index) {
          final book = books[index];
          return Card(
            elevation: 3,
            margin: const EdgeInsets.only(bottom: 10),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: const Color(0xFF3F2E56),
                child: Text('${index + 1}', style: const TextStyle(color: Colors.white)),
              ),
              title: Text(book['name']!, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
              subtitle: const Text('مربوط بالمستودع الشامل (آلاف الأحاديث)'),
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => RepoHadithsScreen(
                      bookName: book['name']!,
                      bookKey: book['key']!,
                    ),
                  ),
                );
              },
            ),
          );
        },
      ),
    );
  }
}

class RepoHadithsScreen extends StatefulWidget {
  final String bookName;
  final String bookKey;

  const RepoHadithsScreen({super.key, required this.bookName, required this.bookKey});

  @override
  State<RepoHadithsScreen> createState() => _RepoHadithsScreenState();
}

class _RepoHadithsScreenState extends State<RepoHadithsScreen> {
  List allHadiths = [];
  List filteredHadiths = [];
  bool isLoading = true;
  bool hasError = false;
  final TextEditingController searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    fetchHadithsFromRepo();
  }

  // جلب الأحاديث مباشرة من مستودع GitHub
  Future<void> fetchHadithsFromRepo() async {
    final url = 'https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/editions/${widget.bookKey}.json';
    try {
      final ByteData data = await NetworkAssetBundle(Uri.parse(url)).load("");
      final String jsonString = utf8.decode(data.buffer.asUint8List());
      final jsonData = jsonDecode(jsonString);

      setState(() {
        allHadiths = jsonData['hadiths'] ?? [];
        filteredHadiths = allHadiths;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        isLoading = false;
        hasError = true;
      });
    }
  }

  void filterSearch(String query) {
    if (query.isEmpty) {
      setState(() {
        filteredHadiths = allHadiths;
      });
    } else {
      setState(() {
        filteredHadiths = allHadiths.where((item) {
          final text = item['text'] ?? '';
          return text.contains(query);
        }).toList();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('${widget.bookName} (${allHadiths.length} حديث)'),
        centerTitle: true,
      ),
      body: Column(
        children: [
          // شريط البحث في الأحاديث
          if (!isLoading && !hasError)
            Padding(
              padding: const EdgeInsets.all(10.0),
              child: TextField(
                controller: searchController,
                onChanged: filterSearch,
                decoration: InputDecoration(
                  hintText: 'ابحث عن كلمة في الأحاديث...',
                  prefixIcon: const Icon(Icons.search),
                  fillColor: Colors.white,
                  filled: true,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                ),
              ),
            ),
          Expanded(
            child: isLoading
                ? const Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        CircularProgressIndicator(color: Colors.white),
                        SizedBox(height: 12),
                        Text('جاري تحميل كافة أحاديث الكتاب من المستودع...',
                            style: TextStyle(color: Colors.white, fontSize: 16)),
                      ],
                    ),
                  )
                : hasError
                    ? const Center(
                        child: Text(
                          'تأكد من اتصالك بالإنترنت لتحميل الأحاديث.',
                          style: TextStyle(color: Colors.white, fontSize: 16),
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        itemCount: filteredHadiths.length,
                        itemBuilder: (context, index) {
                          final item = filteredHadiths[index];
                          return Card(
                            elevation: 2,
                            margin: const EdgeInsets.only(bottom: 12),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            child: Padding(
                              padding: const EdgeInsets.all(16.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                        decoration: BoxDecoration(
                                          color: Colors.teal,
                                          borderRadius: BorderRadius.circular(6),
                                        ),
                                        child: Text(
                                          'حديث رقم: ${item['hadithnumber'] ?? (index + 1)}',
                                          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                                        ),
                                      ),
                                    ],
                                  ),
                                  const Divider(height: 20),
                                  SelectableText(
                                    item['text'] ?? '',
                                    style: const TextStyle(fontSize: 17, height: 1.6, color: Colors.black87),
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }
}
