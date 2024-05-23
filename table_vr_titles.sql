-- Drop vr_title_images table first to avoid foreign key constraint error
DROP TABLE IF EXISTS `vr_title_images`;

-- Drop vr_titles table
DROP TABLE IF EXISTS `vr_titles`;

/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;

-- Create vr_titles table
CREATE TABLE `vr_titles` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(191) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `slug` varchar(191) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `short_description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `primary_image` varchar(191) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `age_rating` varchar(191) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `min_players` int NOT NULL DEFAULT '1',
  `max_players` int NOT NULL DEFAULT '1',
  `store_url` varchar(191) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `featured` tinyint(1) NOT NULL DEFAULT '0',
  `active` tinyint(1) NOT NULL DEFAULT '0',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `steam_id` varchar(191) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `exec_path` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `monitor` tinyint(1) NOT NULL DEFAULT '0',
  `single_player` tinyint(1) NOT NULL DEFAULT '1',
  `multi_player` tinyint(1) NOT NULL DEFAULT '0',
  `is_free` tinyint(1) NOT NULL DEFAULT '0',
  `extended_library` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=390 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create vr_title_images table
CREATE TABLE `vr_title_images` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `vr_title_id` int unsigned NOT NULL,
  `file_path` varchar(191) COLLATE utf8mb3_unicode_ci NOT NULL,
  `primary` tinyint(
1) NOT NULL DEFAULT '0',
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `vr_title_images_vr_title_id_foreign` (`vr_title_id`),
  CONSTRAINT `vr_title_images_vr_title_id_foreign` FOREIGN KEY (`vr_title_id`) REFERENCES `vr_titles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=793 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;

DROP TABLE IF EXISTS `vr_categories`;
CREATE TABLE `vr_categories` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(191) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `vr_title_categories`;
CREATE TABLE `vr_title_categories` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `category_id` int NOT NULL,
  `title_id` int NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1893 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
