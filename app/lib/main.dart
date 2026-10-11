import 'package:flutter/material.dart';

import 'screens/documents_screen.dart';
import 'screens/history_screen.dart';
import 'screens/run_screen.dart';

void main() => runApp(const NexoraApp());

class NexoraApp extends StatelessWidget {
  const NexoraApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NEXORA LifeOS',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: const Color(0xFF3F51B5),
        useMaterial3: true,
      ),
      home: const HomeShell(),
    );
  }
}

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int _index = 0;
  int _historyTick = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('NEXORA LifeOS')),
      body: IndexedStack(
        index: _index,
        children: [
          const RunScreen(),
          HistoryScreen(key: ValueKey(_historyTick)),
          const DocumentsScreen(),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() {
          _index = i;
          if (i == 1) _historyTick++;
        }),
        destinations: const [
          NavigationDestination(
              icon: Icon(Icons.play_circle_outline), label: 'Run'),
          NavigationDestination(icon: Icon(Icons.history), label: 'History'),
          NavigationDestination(
              icon: Icon(Icons.folder_open), label: 'Documents'),
        ],
      ),
    );
  }
}