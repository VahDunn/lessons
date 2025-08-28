PK - кластерный индекс на Region.RegionID

ALTER TABLE Region
    ADD CONSTRAINT PK_Region PRIMARY KEY CLUSTERED (RegionID);

PK - кластерный индекс на Territories.TerritoryID

ALTER TABLE Territories
    ADD CONSTRAINT PK_Territories PRIMARY KEY CLUSTERED (TerritoryID);

Некластерный индекс на Territories.RegionID

CREATE INDEX IX_Territories_RegionID
ON Territories (RegionID);