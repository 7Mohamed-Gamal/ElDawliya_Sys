-- Create the hr_employeetask table with its initial structure
CREATE TABLE [hr_employeetask] (
    [id] BIGINT IDENTITY(1,1) NOT NULL,
    [title] NVARCHAR(200) NOT NULL,
    [description] NVARCHAR(MAX) NOT NULL,
    [status] NVARCHAR(20) NOT NULL,
    [priority] NVARCHAR(20) NOT NULL,
    [start_date] DATE NOT NULL,
    [due_date] DATE NOT NULL,
    [completion_date] DATE NULL,
    [progress] INT NOT NULL,
    [notes] NVARCHAR(MAX) NULL,
    [created_at] DATETIME2 NOT NULL,
    [updated_at] DATETIME2 NOT NULL,
    CONSTRAINT [PK_hr_employeetask] PRIMARY KEY ([id])
);
