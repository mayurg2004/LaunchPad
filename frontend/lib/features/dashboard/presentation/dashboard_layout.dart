import 'package:flutter/material.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';
import 'package:responsive_builder/responsive_builder.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../notifications/presentation/notification_panel.dart';
import '../../notifications/providers/notification_provider.dart';
import 'dashboard_screen.dart';
import '../../placement_drives/presentation/placement_drives_screen.dart';
import '../../applications/presentation/applications_screen.dart';
import '../../placement_drives/providers/application_provider.dart';
import '../../../core/api/api_client.dart';

class DashboardLayout extends StatefulWidget {
  const DashboardLayout({super.key});

  @override
  State<DashboardLayout> createState() => _DashboardLayoutState();
}

class _DashboardLayoutState extends State<DashboardLayout> {
  int _selectedIndex = 0;

  final List<_NavigationItem> _navItems = [
    _NavigationItem(title: 'Dashboard', icon: LucideIcons.layoutDashboard),
    _NavigationItem(title: 'Placement Drives', icon: LucideIcons.briefcase),
    _NavigationItem(title: 'Applications', icon: LucideIcons.fileText),
    _NavigationItem(title: 'Interviews', icon: LucideIcons.calendarDays),
    _NavigationItem(title: 'Offers', icon: LucideIcons.award),
    _NavigationItem(title: 'Resume', icon: LucideIcons.fileBadge2),
    _NavigationItem(title: 'AI Career', icon: LucideIcons.sparkles),
  ];

  @override
  Widget build(BuildContext context) {
    return ResponsiveBuilder(
      builder: (context, sizingInformation) {
        bool isDesktop = sizingInformation.deviceScreenType == DeviceScreenType.desktop;
        
        return Scaffold(
          appBar: _buildTopBar(isDesktop),
          drawer: !isDesktop ? _buildDrawer() : null,
          endDrawer: const NotificationPanel(),
          body: Row(
            children: [
              if (isDesktop) _buildSidebar(),
              Expanded(
                child: _buildCurrentScreen(),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildCurrentScreen() {
    switch (_selectedIndex) {
      case 0:
        return const DashboardScreen();
      case 1:
        return const PlacementDrivesScreen();
      case 2:
        return ApplicationsScreen(
          onBrowseOpportunities: () {
            setState(() => _selectedIndex = 1);
          },
        );
      // Add other screens as needed
      default:
        return const Center(child: Text('Coming soon...'));
    }
  }

  PreferredSizeWidget _buildTopBar(bool isDesktop) {
    return AppBar(
      title: isDesktop 
          ? const SizedBox.shrink()
          : Row(
              children: [
                const Icon(LucideIcons.rocket, color: AppColors.primary),
                const SizedBox(width: AppSpacing.sm),
                Text('LaunchPad', style: Theme.of(context).textTheme.titleLarge?.copyWith(color: AppColors.primary)),
              ],
            ),
      actions: [
        IconButton(
          icon: const Icon(LucideIcons.search),
          onPressed: () {},
        ),
        Consumer(
          builder: (context, ref, child) {
            final unreadCount = ref.watch(unreadCountProvider);
            return IconButton(
              icon: Badge(
                isLabelVisible: unreadCount > 0,
                label: Text('$unreadCount'),
                backgroundColor: AppColors.error,
                child: const Icon(LucideIcons.bell),
              ),
              onPressed: () {
                Scaffold.of(context).openEndDrawer();
              },
            );
          },
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md),
          child: CircleAvatar(
            backgroundColor: AppColors.surfaceElevated,
            child: Text(
              'MS',
              style: Theme.of(context).textTheme.labelLarge?.copyWith(color: AppColors.primary),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildDrawer() {
    return Drawer(
      backgroundColor: AppColors.background,
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(AppSpacing.xl),
            child: Row(
              children: [
                const Icon(LucideIcons.rocket, color: AppColors.primary, size: 32),
                const SizedBox(width: AppSpacing.sm),
                Expanded(
                  child: Text('LaunchPad', style: Theme.of(context).textTheme.headlineMedium?.copyWith(color: AppColors.primary), maxLines: 1, overflow: TextOverflow.ellipsis),
                ),
              ],
            ),
          ),
          Expanded(child: _buildNavList()),
        ],
      ),
    );
  }

  Widget _buildSidebar() {
    return Container(
      width: 260,
      decoration: const BoxDecoration(
        color: AppColors.surface,
        border: Border(
          right: BorderSide(color: AppColors.border, width: 1),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(AppSpacing.xl),
            child: Row(
              children: [
                const Icon(LucideIcons.rocket, color: AppColors.primary, size: 32),
                const SizedBox(width: AppSpacing.sm),
                Expanded(
                  child: Text('LaunchPad', style: Theme.of(context).textTheme.headlineMedium?.copyWith(color: AppColors.primary), maxLines: 1, overflow: TextOverflow.ellipsis),
                ),
              ],
            ),
          ),
          Expanded(child: _buildNavList()),
          const Divider(color: AppColors.border),
          _buildNavItem(_NavigationItem(title: 'Settings', icon: LucideIcons.settings), _navItems.length, false),
          _buildNavItem(_NavigationItem(title: 'Logout', icon: LucideIcons.logOut), _navItems.length + 1, false),
          const SizedBox(height: AppSpacing.md),
        ],
      ),
    );
  }

  Widget _buildNavList() {
    return ListView.builder(
      itemCount: _navItems.length,
      itemBuilder: (context, index) {
        return _buildNavItem(_navItems[index], index, true);
      },
    );
  }

  Widget _buildNavItem(_NavigationItem item, int index, bool isMain) {
    bool isSelected = isMain && _selectedIndex == index;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: AppSpacing.xs),
      child: InkWell(
        onTap: () {
          if (isMain) {
            setState(() => _selectedIndex = index);
          } else if (item.title == 'Logout') {
            ApiClient.logout();
          }
        },
        borderRadius: BorderRadius.circular(AppSpacing.buttonRadius),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(horizontal: AppSpacing.md, vertical: AppSpacing.md),
          decoration: BoxDecoration(
            color: isSelected ? AppColors.primary.withValues(alpha: 0.1) : Colors.transparent,
            borderRadius: BorderRadius.circular(AppSpacing.buttonRadius),
            border: Border.all(
              color: isSelected ? AppColors.primary.withValues(alpha: 0.2) : Colors.transparent,
            )
          ),
          child: Row(
            children: [
              Icon(
                item.icon,
                size: 20,
                color: isSelected ? AppColors.primary : AppColors.textSecondary,
              ),
              const SizedBox(width: AppSpacing.md),
              Expanded(
                child: Text(
                  item.title,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(context).textTheme.labelLarge?.copyWith(
                    color: isSelected ? AppColors.primary : AppColors.textSecondary,
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                  ),
                ),
              ),
              if (item.title == 'Applications')
                Consumer(
                  builder: (context, ref, child) {
                    final applicationsAsync = ref.watch(myApplicationsProvider);
                    return applicationsAsync.when(
                      data: (applications) {
                        if (applications.isEmpty) return const SizedBox.shrink();
                        final count = applications.length;
                        return Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: AppColors.primary,
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            count > 99 ? '99+' : count.toString(),
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        );
                      },
                      loading: () => const SizedBox.shrink(),
                      error: (_, _) => const SizedBox.shrink(),
                    );
                  },
                ),
            ],
          ),
        ),
      ),
    );
  }
}

class _NavigationItem {
  final String title;
  final IconData icon;

  _NavigationItem({required this.title, required this.icon});
}
