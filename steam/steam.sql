CREATE TABLE IF NOT EXISTS `Apps`(
    `AppID`         int(7) unsigned NOT NULL,
    `Name`          varchar(255),
    `Description`   varchar(20000),
    `Price`         int(7),
    `InDiscount`    int(1),
    `LastUpdated`   timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`AppID`),
    INDEX appid_index (`AppID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `DiscountApps`(
    `AppID`             int(7) unsigned NOT NULL,
    `DiscountPercent`   int(3),
    `OriginalPrice`     int(7),
    `FinalPrice`        int(7),
    `LastUpdated`   timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`AppID`),
    INDEX appid_index (`AppID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
