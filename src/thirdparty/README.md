# External Dependencies (Managed by vcstool)

This directory contains third-party ROS 2 packages required by Sky Warrior.

## DO NOT manually clone packages here!

Instead, use vcstool to import dependencies from `../../dependencies.repos`:

```bash
# From workspace root (~/sky_warrior_ws)
vcs import src/thirdparty < dependencies.repos

# Update existing packages
vcs pull src/thirdparty
```

## Current Dependencies

- **px4_msgs**: PX4 message definitions for ROS 2
- **px4_ros_com**: PX4-ROS 2 communication bridge utilities

## Adding New Dependencies

Edit `../../dependencies.repos` (workspace root) and add:

```yaml
package_name:
  type: git
  url: https://github.com/org/repo.git
  version: main  # or specific tag/branch
```

Then from workspace root run: `vcs import src/thirdparty < dependencies.repos`
