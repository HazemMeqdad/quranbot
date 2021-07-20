CREATE TABLE if not exists `guilds` (
  `id` bigint(30) PRIMARY KEY,
  `guild_name` varchar(25) DEFAULT NULL,
  `prefix` text DEFAULT '!',
  `channel` bigint(30) DEFAULT NULL,
  `time` int(11) DEFAULT 3600 CHECK (`time` >= 1800 and `time` <= 86400),
  `anti_spam` tinyint(1) DEFAULT 0,
  `embed` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS blacklist(
    id BIGINT(30) PRIMARY KEY,
    mod_id BIGINT(30) NOT NULL,
    reason VARCHAR(30) DEFAULT NULL,
    timestamp BIGINT(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `azkar`(
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `msg` TEXT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
