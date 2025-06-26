-- MySQL dump 10.13  Distrib 8.0.40, for macos14 (arm64)
--
-- Host: localhost    Database: fastapi-vue3-antd-zanyuh-admin-1.2
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `sys_admin`
--

DROP TABLE IF EXISTS `sys_admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_admin` (
  `id` int NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL DEFAULT '1',
  `username` varchar(20) NOT NULL,
  `nickname` varchar(50) NOT NULL,
  `password` varchar(128) NOT NULL,
  `avatar` varchar(255) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `mobile` varchar(11) NOT NULL,
  `login_failure` int NOT NULL DEFAULT '0',
  `login_at` datetime DEFAULT NULL,
  `login_ip` varchar(50) DEFAULT NULL,
  `token` varchar(512) DEFAULT NULL,
  `status` enum('normal','hidden') NOT NULL DEFAULT 'normal',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username_UNIQUE` (`username`),
  UNIQUE KEY `mobile_UNIQUE` (`mobile`),
  UNIQUE KEY `email_UNIQUE` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_admin`
--

LOCK TABLES `sys_admin` WRITE;
/*!40000 ALTER TABLE `sys_admin` DISABLE KEYS */;
INSERT INTO `sys_admin` VALUES (1,1,'admin','SupperAdmin','$2b$12$cw3xuR7n.Cid4CZdchXIp.x0H4t5SKKDOq06lwZOhfAxCAd7Pi3p6',NULL,'13800000000@qq.com','13800000000',0,'2025-06-25 23:02:17','127.0.0.1','eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzUxNDk3MzM2fQ.BmJsP6wIBWutRfScL6rOgdPGV4eoBNmPaBNcHVm-jgs','normal','2025-05-15 23:49:04','2025-06-25 23:02:17');
/*!40000 ALTER TABLE `sys_admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_admin_group`
--

DROP TABLE IF EXISTS `sys_admin_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_admin_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `pid` int NOT NULL DEFAULT '0',
  `name` varchar(100) NOT NULL,
  `rules` json NOT NULL,
  `access` json NOT NULL,
  `status` enum('normal','hidden') NOT NULL DEFAULT 'normal',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_admin_group`
--

LOCK TABLES `sys_admin_group` WRITE;
/*!40000 ALTER TABLE `sys_admin_group` DISABLE KEYS */;
INSERT INTO `sys_admin_group` VALUES (1,1,'super','[\"all\"]','[\"all\"]','normal','2024-04-05 12:15:11','2025-03-04 15:54:49');
/*!40000 ALTER TABLE `sys_admin_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_admin_log`
--

DROP TABLE IF EXISTS `sys_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `admin_id` int NOT NULL,
  `username` varchar(30) NOT NULL,
  `url` varchar(1500) NOT NULL,
  `title` varchar(100) DEFAULT NULL,
  `content` text NOT NULL,
  `ip` varchar(50) NOT NULL,
  `useragent` text,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_admin_log`
--

LOCK TABLES `sys_admin_log` WRITE;
/*!40000 ALTER TABLE `sys_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `sys_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_admin_rule`
--

DROP TABLE IF EXISTS `sys_admin_rule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_admin_rule` (
  `id` int NOT NULL AUTO_INCREMENT,
  `rule_type` enum('menu','action') NOT NULL DEFAULT 'menu',
  `parent_id` int NOT NULL DEFAULT '0',
  `name` varchar(150) NOT NULL,
  `path` varchar(50) NOT NULL,
  `component` varchar(200) DEFAULT NULL,
  `redirect` varchar(100) DEFAULT NULL,
  `meta` json DEFAULT NULL,
  `permission` json DEFAULT NULL,
  `menu_display_type` enum('ajax','addtabs','blank','dialog') DEFAULT 'addtabs',
  `model_name` varchar(80) NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `weigh` int NOT NULL DEFAULT '0',
  `status` enum('normal','hidden','deleted') NOT NULL DEFAULT 'normal',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_admin_rule`
--

LOCK TABLES `sys_admin_rule` WRITE;
/*!40000 ALTER TABLE `sys_admin_rule` DISABLE KEYS */;
INSERT INTO `sys_admin_rule` VALUES (1,'menu',0,'dashboard','/admin','/_core/dashboard/dashboard','/dashboard','{\"icon\": \"mdi:view-dashboard-outline\", \"title\": \"dashboard.dashboard\"}','{}','addtabs','Dashboard',NULL,1,'normal','2024-01-22 14:32:00','2025-03-04 10:59:45'),(2,'menu',1,'├ workspace','/dashboard/workspace','/_core/dashboard/workspace/index',NULL,'{\"icon\": \"mdi:view-dashboard-outline\", \"title\": \"dashboard.workspace.workspace\"}','{\"view\": true}','addtabs','Dashboard',NULL,1,'normal','2024-01-22 14:32:00','2025-06-05 00:22:17'),(3,'menu',0,'generals','/generals',NULL,NULL,'{\"icon\": \"mdi:cog-outline\", \"title\": \"general.general\"}','{}','addtabs','Generals',NULL,2,'normal','2024-01-22 14:32:00','2025-02-28 18:40:34'),(4,'menu',3,'general.profile','/general/profile','/_core/general/profile',NULL,'{\"icon\": \"mdi:account-outline\", \"title\": \"general.profile.profile\"}','{\"edit\": true}','addtabs','GeneralProfile',NULL,11,'normal','2024-01-22 14:32:00','2025-02-28 12:04:00'),(5,'menu',3,'general.category','/general/category','/_core/general/category','','{\"icon\": \"mdi:category-plus-outline\", \"title\": \"general.category.category\", \"menuVisibleWithForbidden\": \"false\"}','{\"add\": true, \"edit\": true, \"view\": true, \"delete\": true}','ajax','GeneralsCategory',NULL,0,'normal','2025-03-04 03:24:40','2025-03-07 11:12:12'),(6,'menu',3,'general.config','/general/config','/_core/general/config',NULL,'{\"icon\": \"mdi:cog-outline\", \"title\": \"general.config.config\"}','{\"add\": true, \"edit\": true, \"delete\": true}','addtabs','GeneralConfig',NULL,8,'normal','2024-01-22 14:32:00','2025-03-04 07:36:31'),(7,'menu',0,'attachments','/attachments',NULL,NULL,'{\"icon\": \"mdi:paperclip\", \"title\": \"attachment.attachment_manage\"}','{}','blank','Attachment',NULL,9,'normal','2024-01-22 14:32:00','2025-03-06 11:39:00'),(8,'menu',7,'attachment.attachment','/attachment/attachment','/_core/attachment/attachment',NULL,'{\"icon\": \"mdi:file-outline\", \"title\": \"attachment.attachment\"}','{\"add\": true, \"edit\": true, \"view\": true, \"delete\": true}','addtabs','Attachment',NULL,10,'normal','2024-01-22 14:32:00','2025-03-06 11:39:00'),(9,'menu',0,'plugins','/plugins',NULL,NULL,'{\"icon\": \"mdi:puzzle-outline\", \"title\": \"plugin.plugin\", \"childComponent\": \"/_core/general/profile\"}','{}','addtabs','Plugin',NULL,3,'normal','2024-01-22 14:32:00','2025-02-28 17:51:12'),(10,'menu',0,'admin','/admin',NULL,NULL,'{\"icon\": \"mdi:shield-account-outline\", \"title\": \"admin.admin.field.admin\"}','{}','addtabs','Admin',NULL,4,'normal','2024-01-22 14:32:00','2025-06-04 12:15:36'),(11,'menu',10,'admin.admin','/admin/admin','/_core/admin/admin',NULL,'{\"icon\": \"mdi:account-outline\", \"title\": \"admin.admin.admin_manage\"}','{\"add\": true, \"ajax\": true, \"edit\": true, \"view\": true, \"delete\": true}','addtabs','Admin',NULL,20,'normal','2024-01-22 14:32:00','2025-03-06 16:24:24'),(12,'menu',10,'admin.group','/admin/group','/_core/admin/group',NULL,'{\"icon\": \"mdi:account-group-outline\", \"title\": \"admin.group.group\"}','{\"add\": true, \"ajax\": true, \"edit\": true, \"view\": true, \"delete\": true}','addtabs','AdminGroup',NULL,21,'normal','2024-01-22 14:32:00','2025-03-06 13:03:05'),(13,'menu',10,'admin.rule','/admin/rule','/_core/admin/rule',NULL,'{\"icon\": \"mdi:shield-account-outline\", \"title\": \"admin.rule.rule\"}','{\"add\": true, \"edit\": true, \"view\": true, \"delete\": true}','addtabs','AdminRule',NULL,47,'normal','2024-01-22 14:32:00','2025-03-06 13:03:05'),(14,'menu',10,'admin.log','/admin/log','/_core/admin/log',NULL,'{\"icon\": \"mdi:clipboard-text-outline\", \"title\": \"admin.log.log\"}','{\"view\": true}','addtabs','AdminLog',NULL,50,'normal','2024-01-22 14:32:00','2025-03-04 07:36:31'),(15,'menu',0,'users','/users',NULL,NULL,'{\"icon\": \"mdi:account-multiple-outline\", \"title\": \"user.user\"}','{}','addtabs','Users',NULL,24,'normal','2024-01-22 14:32:00','2025-02-26 17:47:48'),(16,'menu',15,'user','/user','/_core/user/user',NULL,'{\"icon\": \"mdi:account-outline\", \"title\": \"user.user_manage\"}','{\"add\": true, \"edit\": true, \"view\": true, \"delete\": true}','addtabs','User',NULL,24,'normal','2024-01-22 14:32:00','2025-03-06 16:19:59'),(17,'menu',15,'user.rule','/user/rule','/_core/user/rule',NULL,'{\"icon\": \"mdi:shield-account-outline\", \"title\": \"user.rule.rule\"}','{\"add\": true, \"edit\": true, \"view\": true, \"delete\": true}','addtabs','UserRule',NULL,26,'normal','2024-01-22 14:32:00','2025-03-04 07:36:31'),(18,'menu',15,'user.balance.log','/user/balance/log','/_core/user/balance_log',NULL,'{\"icon\": \"mdi:account-balance-wallet-outline\", \"title\": \"user.balance_log.balance_log\"}','{\"add\": true, \"edit\": true, \"view\": true, \"delete\": true}','addtabs','UserBalance',NULL,25,'normal','2024-01-22 14:32:00','2025-03-06 16:27:28'),(19,'menu',15,'user.score.log','/user/score/log','/_core/user/score_log',NULL,'{\"icon\": \"mdi:scoreboard-outline\", \"title\": \"user.score_log.score_log\"}','{\"add\": true, \"edit\": true, \"view\": true, \"delete\": true}','addtabs','UserScore',NULL,25,'normal','2024-01-22 14:32:00','2025-03-06 16:28:37'),(20,'menu',15,'user.group','/user/group','/_core/user/group',NULL,'{\"icon\": \"mdi:account-group-outline\", \"title\": \"user.group.group\"}','{\"add\": true, \"edit\": true, \"view\": true, \"delete\": true}','addtabs','UserGroup',NULL,0,'normal','2024-09-26 13:01:14','2025-03-04 07:36:31'),(22,'menu',9,'generator','/plugins/generator','/plugins/generator','','{\"icon\": \"mdi:codepen\", \"title\": \"generator.code_generator\", \"menuVisibleWithForbidden\": \"false\"}','{\"view\": true}','ajax','generator',NULL,0,'normal','2025-02-28 10:31:33','2025-03-04 07:36:31'),(24,'menu',7,'attachmentCategory','/attachment/category','/_core/attachment/category','','{\"icon\": \"mdi:attachment\", \"title\": \"attachment.category.category\", \"menuVisibleWithForbidden\": \"false\"}','{\"add\": true, \"edit\": true, \"view\": true, \"delete\": true}','ajax','attachmentCategory',NULL,0,'normal','2025-03-06 03:54:07','2025-03-06 12:56:31'),(25,'menu',9,'plugin','/plugin/plugin','/_core/plugin/plugin','','{\"icon\": \"mdi:shape-rectangle-add\", \"title\": \"plugin.plugin\", \"menuVisibleWithForbidden\": \"false\"}','{\"add\": true, \"edit\": true, \"view\": true, \"delete\": true}','ajax','plugin',NULL,0,'normal','2025-03-09 02:40:04','2025-03-09 11:05:32'),(26,'menu',9,'plugin_store','/plugin/plugin_store','/_core/plugin_store','','{\"icon\": \"mdi:all-inclusive\", \"title\": \"plugin.plugin_store\", \"menuVisibleWithForbidden\": \"false\"}','{\"enable\": true, \"disable\": true, \"install\": true, \"unstall\": true}','ajax','online_plugin',NULL,0,'normal','2025-03-10 07:15:54','2025-03-10 16:07:41'),(27,'menu',1,'analytics','/dashboard/analytics','/_core/dashboard/analytics/index',NULL,'{\"icon\": \"mdi:view-dashboard-outline\", \"title\": \"dashboard.analytics\"}','{\"view\": true}','addtabs','Dashboard',NULL,1,'normal','2024-01-22 14:32:00','2025-03-04 07:36:31');
/*!40000 ALTER TABLE `sys_admin_rule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_analytics_metrics`
--

DROP TABLE IF EXISTS `sys_analytics_metrics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_analytics_metrics` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT 'Primary key ID',
  `record_date` date NOT NULL COMMENT 'Record date (YYYY-MM-DD)',
  `user_count` bigint unsigned NOT NULL DEFAULT '0' COMMENT 'Daily active users',
  `total_users` bigint unsigned NOT NULL DEFAULT '0' COMMENT 'Cumulative total users',
  `visit_count` bigint unsigned NOT NULL DEFAULT '0' COMMENT 'Daily visits',
  `total_visits` bigint unsigned NOT NULL DEFAULT '0' COMMENT 'Cumulative total visits',
  `download_count` bigint unsigned NOT NULL DEFAULT '0' COMMENT 'Daily downloads',
  `total_downloads` bigint unsigned NOT NULL DEFAULT '0' COMMENT 'Cumulative total downloads',
  `usage_count` bigint unsigned NOT NULL DEFAULT '0' COMMENT 'Daily active usage sessions',
  `total_usage` bigint unsigned NOT NULL DEFAULT '0' COMMENT 'Cumulative total usage sessions',
  `source` enum('web','app','mobile_web','api','other') DEFAULT NULL COMMENT 'Traffic source (web, mobile app, etc)',
  `device_type` enum('mobile','desktop','tablet','smart_tv','other') DEFAULT NULL COMMENT 'User device type',
  `region` varchar(50) DEFAULT NULL COMMENT 'Geographical region/country',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation timestamp',
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Record last update timestamp',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_date_dimensions` (`record_date`,`source`,`device_type`,`region`),
  KEY `idx_date` (`record_date`),
  KEY `idx_region` (`region`),
  KEY `idx_source` (`source`),
  KEY `idx_device` (`device_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Unified analytics metrics table';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_analytics_metrics`
--

LOCK TABLES `sys_analytics_metrics` WRITE;
/*!40000 ALTER TABLE `sys_analytics_metrics` DISABLE KEYS */;
/*!40000 ALTER TABLE `sys_analytics_metrics` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_attachment`
--

DROP TABLE IF EXISTS `sys_attachment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_attachment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cat_id` int DEFAULT '0',
  `admin_id` int NOT NULL,
  `user_id` int NOT NULL,
  `att_type` enum('image','file') DEFAULT 'image',
  `thumb` varchar(255) DEFAULT NULL,
  `path_file` varchar(255) NOT NULL,
  `file_name` varchar(100) DEFAULT NULL,
  `file_size` int NOT NULL,
  `mimetype` varchar(100) DEFAULT NULL,
  `ext_param` varchar(255) DEFAULT NULL,
  `storage` varchar(100) NOT NULL,
  `sha1` varchar(40) DEFAULT NULL,
  `general_attachment_col` varchar(45) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_attachment`
--

LOCK TABLES `sys_attachment` WRITE;
/*!40000 ALTER TABLE `sys_attachment` DISABLE KEYS */;
INSERT INTO `sys_attachment` VALUES (1,0,1,0,'image',NULL,'/uploads/avatar/avatar_1_3c1726.png','avatar_1_3c1726.png',51885,'image/jpeg','ext_param','local','ce58f022889896037c547890e95163a1b0fd86cb','some_value','2025-03-07 04:09:35','2025-03-07 04:09:35'),(2,0,1,0,'image',NULL,'/uploads/avatar/avatar_1_1644fd.png','avatar_1_1644fd.png',47281,'image/jpeg','ext_param','local','f43d9dfb6f2ccdb955e81fc9bc4176e885368eac','some_value','2025-04-30 02:16:56','2025-04-30 02:16:56');
/*!40000 ALTER TABLE `sys_attachment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_attachment_category`
--

DROP TABLE IF EXISTS `sys_attachment_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_attachment_category` (
  `id` int NOT NULL AUTO_INCREMENT,
  `pid` int NOT NULL DEFAULT '0',
  `name` varchar(30) NOT NULL,
  `status` enum('normal','hidden') NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_attachment_category`
--

LOCK TABLES `sys_attachment_category` WRITE;
/*!40000 ALTER TABLE `sys_attachment_category` DISABLE KEYS */;
INSERT INTO `sys_attachment_category` VALUES (1,0,'default','normal','2025-03-06 12:00:02','2025-03-07 09:10:48');
/*!40000 ALTER TABLE `sys_attachment_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_general_category`
--

DROP TABLE IF EXISTS `sys_general_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_general_category` (
  `id` int NOT NULL AUTO_INCREMENT,
  `pid` int NOT NULL,
  `type` varchar(30) NOT NULL,
  `name` varchar(30) NOT NULL,
  `thumb` varchar(100) DEFAULT NULL,
  `keywords` varchar(255) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `weigh` int NOT NULL,
  `status` enum('normal','hidden') NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_general_category`
--

LOCK TABLES `sys_general_category` WRITE;
/*!40000 ALTER TABLE `sys_general_category` DISABLE KEYS */;
INSERT INTO `sys_general_category` VALUES (1,0,'default','default','','','',0,'normal','2024-05-08 17:19:06','2025-03-07 11:50:19'),(2,0,'blog','news','','','',0,'normal','2025-06-04 17:47:14','2025-06-04 17:47:14');
/*!40000 ALTER TABLE `sys_general_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_general_config`
--

DROP TABLE IF EXISTS `sys_general_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_general_config` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `group` varchar(30) NOT NULL,
  `title` varchar(100) NOT NULL,
  `tip` varchar(100) DEFAULT NULL,
  `type` varchar(30) DEFAULT NULL,
  `visible` varchar(255) DEFAULT NULL,
  `value` text,
  `content` text,
  `rule` varchar(100) DEFAULT NULL,
  `extend` varchar(255) DEFAULT NULL,
  `setting` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_general_config`
--

LOCK TABLES `sys_general_config` WRITE;
/*!40000 ALTER TABLE `sys_general_config` DISABLE KEYS */;
INSERT INTO `sys_general_config` VALUES (1,'name','basic','Site name','Please Input  Site name','string','','栈鱼后台管理系统Pro 1.0','','required','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(2,'copyright','basic','Copyright','Please Input  Copyright','string','','Copyright © 2024 <a href=\"https://admin-panel.zhanor.com\" class=\"text-subtitle-2\">栈鱼后台管理系统 1.0</a>. All rights reserved.','','','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(3,'cdnurl','basic','Cdn url','Please Input  Site name','string','','https://zhanor.com','','','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(4,'version','basic','Version','Please Input  Version','string','','1.0.1','','required','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(5,'timezone','basic','Timezone','','string','','Asia/Shanghai','','required','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(6,'forbiddenip','basic','Forbidden ip','Please Input  Forbidden ip','text','','12.23.21.1\n1.2.3.6\n34.78.43.1','','','','','2025-04-29 07:12:13','2025-04-29 07:12:13'),(7,'languages','basic','Languages','','array','','{\"frontend\": \"zh-cn\", \"backend\": \"zh-cn\"}','','required','','','2024-12-29 01:39:29','2024-12-29 01:39:29'),(8,'fixedpage','basic','Fixed page','Please Input Fixed page','string','','dashboard','','required','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(9,'categorytype','dictionary','Category type','','array','','{\"default\": \"Default\", \"page\": \"Page\", \"article\": \"Article\"}','','','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(11,'mail_type','email','Mail type','Please Input Mail type','select','','SMTP','[\"Please Select\",\"SMTP\"]','','','','2024-12-29 01:39:29','2024-12-29 20:59:28'),(12,'mail_smtp_host','email','Mail smtp host','Please Input Mail smtp host','string','','smtp.qq.com','','','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(13,'mail_smtp_port','email','Mail smtp port','Please Input  Mail smtp port(default25,SSL：465,TLS：587)','string','','465','','','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(14,'mail_smtp_user','email','Mail smtp user','Please Input Mail smtp user','string','','10000','','','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(15,'mail_smtp_pass','email','Mail smtp password','Please Input  Mail smtp password','string','','password','','','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(16,'mail_verify_type','email','Mail vertify type','Please Input Mail vertify type','select','','TLS','[\"None\",\"TLS\",\"SSL\"]','','','','2024-12-29 01:39:29','2024-12-29 20:58:05'),(17,'mail_from','email','Mail from','','string','','10000@qq.com','','','','','2024-12-29 01:39:29','2024-12-27 11:57:06'),(18,'image_category','dictionary','Attachment Image category','','array','','{\"default\": \"Default\", \"blog\": \"Blog\"}','','','','','2024-12-29 01:39:29','2024-12-29 01:39:29'),(19,'file_category','dictionary','Attachment File category','','array','','{\"default\": \"Default\", \"product\": \"Product\"}','','','','','2024-12-29 01:39:29','2024-12-29 01:39:29'),(23,'user_page_title','user','User Page Title','User Page Title','string','','User Center','','letters','','','2024-12-29 01:39:29','2024-12-30 12:50:59'),(24,'user_footer','user','User Center Footer','User Center Footer','text','','Copyright © 2024 <a href=\"https://admin-panel-pro.zhanor.com\" class=\"link-secondary\">会员中心</a>. All rights reserved.','','required','','','2024-12-29 01:39:29','2024-12-30 12:50:59');
/*!40000 ALTER TABLE `sys_general_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_plugin`
--

DROP TABLE IF EXISTS `sys_plugin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_plugin` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(120) NOT NULL,
  `author` varchar(80) NOT NULL,
  `uuid` varchar(120) NOT NULL,
  `description` varchar(255) NOT NULL,
  `version` varchar(50) NOT NULL,
  `downloads` int NOT NULL DEFAULT '0',
  `download_url` varchar(255) NOT NULL,
  `md5_hash` varchar(32) NOT NULL,
  `price` decimal(10,2) NOT NULL DEFAULT '0.00',
  `paid` enum('1','0') NOT NULL DEFAULT '0',
  `installed` enum('1','0') NOT NULL DEFAULT '0',
  `enabled` enum('1','0') NOT NULL DEFAULT '0',
  `setting_menu` json NOT NULL,
  `status` enum('normal','hidden') NOT NULL DEFAULT 'normal',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid_UNIQUE` (`uuid`),
  UNIQUE KEY `title_UNIQUE` (`title`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_plugin`
--

LOCK TABLES `sys_plugin` WRITE;
/*!40000 ALTER TABLE `sys_plugin` DISABLE KEYS */;
INSERT INTO `sys_plugin` VALUES (2,'代码生成器','StkFish','generator','generator','1.0.1',12,'2','2',10.00,'0','1','1','0','normal','2025-03-10 17:09:22','2025-05-09 09:34:40');
/*!40000 ALTER TABLE `sys_plugin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_user`
--

DROP TABLE IF EXISTS `sys_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_group_id` int NOT NULL DEFAULT '1',
  `username` varchar(32) NOT NULL,
  `nickname` varchar(50) NOT NULL,
  `password` varchar(120) NOT NULL,
  `email` varchar(100) NOT NULL,
  `mobile` varchar(16) NOT NULL,
  `avatar` varchar(255) DEFAULT NULL,
  `level` smallint NOT NULL DEFAULT '0',
  `gender` enum('male','female') NOT NULL DEFAULT 'male',
  `birthday` date DEFAULT NULL,
  `bio` varchar(100) DEFAULT 'No  Data',
  `balance` decimal(10,2) DEFAULT '0.00',
  `score` int NOT NULL DEFAULT '0',
  `successions` int DEFAULT '0',
  `max_successions` int DEFAULT '0',
  `prev_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `login_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `login_ip` varchar(50) DEFAULT NULL,
  `login_failure` smallint DEFAULT '0',
  `join_ip` varchar(50) DEFAULT NULL,
  `verification` varchar(255) DEFAULT NULL,
  `token` varchar(250) DEFAULT NULL,
  `status` enum('normal','hidden','delete') DEFAULT 'normal',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username_UNIQUE` (`username`),
  UNIQUE KEY `email_UNIQUE` (`email`),
  UNIQUE KEY `mobile_UNIQUE` (`mobile`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_user`
--

LOCK TABLES `sys_user` WRITE;
/*!40000 ALTER TABLE `sys_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `sys_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_user_balance_log`
--

DROP TABLE IF EXISTS `sys_user_balance_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user_balance_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `balance` decimal(10,0) NOT NULL,
  `before` decimal(10,0) NOT NULL,
  `after` decimal(10,0) NOT NULL,
  `memo` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_user_balance_log`
--

LOCK TABLES `sys_user_balance_log` WRITE;
/*!40000 ALTER TABLE `sys_user_balance_log` DISABLE KEYS */;
INSERT INTO `sys_user_balance_log` VALUES (1,9,888,0,0,'000','2025-03-06 15:58:56','2025-03-06 15:58:56');
/*!40000 ALTER TABLE `sys_user_balance_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_user_group`
--

DROP TABLE IF EXISTS `sys_user_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `rules` varchar(512) NOT NULL,
  `status` enum('normal','hidden') NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_user_group`
--

LOCK TABLES `sys_user_group` WRITE;
/*!40000 ALTER TABLE `sys_user_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `sys_user_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_user_rule`
--

DROP TABLE IF EXISTS `sys_user_rule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user_rule` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` enum('menu','action') NOT NULL,
  `pid` int NOT NULL,
  `plugin` smallint NOT NULL,
  `name` varchar(150) NOT NULL,
  `path` varchar(50) NOT NULL,
  `title` varchar(50) NOT NULL,
  `description` varchar(500) DEFAULT NULL,
  `icon` varchar(50) DEFAULT NULL,
  `menutype` enum('addtabs','blank','dialog','ajax') DEFAULT NULL,
  `extend` varchar(255) DEFAULT NULL,
  `model_name` varchar(50) NOT NULL,
  `weigh` int NOT NULL,
  `status` enum('normal','hidden') NOT NULL DEFAULT 'normal',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_user_rule`
--

LOCK TABLES `sys_user_rule` WRITE;
/*!40000 ALTER TABLE `sys_user_rule` DISABLE KEYS */;
INSERT INTO `sys_user_rule` VALUES (1,'menu',0,0,'user.dashboard','/user/dashboard','User Dashboard','User Dashboard','ti ti-hexagonal-prism',NULL,NULL,'',1,'normal','2024-04-01 09:53:30','2024-04-01 15:19:07'),(2,'menu',0,0,'user.profile','/user/profile','Profile','','ti ti-alert-square-rounded',NULL,NULL,'',0,'normal','2024-04-01 10:08:49','2024-04-01 12:50:48'),(3,'menu',0,0,'user.balance.log','/user/balance/log','Balance Log','','ti ti-color-swatch',NULL,NULL,'',0,'normal','2024-04-01 10:09:32','2024-04-01 13:11:04'),(4,'menu',0,0,'user.score.log','/user/score/log','Score Log','','ti ti-align-right',NULL,NULL,'',0,'normal','2024-04-01 10:10:03','2024-04-01 13:17:28'),(5,'action',0,0,'user.logout','/user/logout','Logout','','ti ti-location-share',NULL,NULL,'',0,'normal','2024-04-01 10:11:22','2024-04-01 13:17:42'),(6,'action',2,0,'user.profile.save','/user/profile/save','Profile Save','','',NULL,NULL,'',0,'normal','2024-04-01 10:21:23','2024-04-01 10:21:23');
/*!40000 ALTER TABLE `sys_user_rule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_user_score_log`
--

DROP TABLE IF EXISTS `sys_user_score_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user_score_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `score` int NOT NULL,
  `before` int NOT NULL,
  `after` int NOT NULL,
  `memo` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_user_score_log`
--

LOCK TABLES `sys_user_score_log` WRITE;
/*!40000 ALTER TABLE `sys_user_score_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `sys_user_score_log` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-26  8:14:51
