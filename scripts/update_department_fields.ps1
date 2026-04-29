# PowerShell script to update Department field references
# This script replaces old org.Department field names with new core.models.hr.Department field names

$ErrorActionPreference = "Continue"

Write-Host "=== Updating Department Field References ===" -ForegroundColor Cyan
Write-Host ""

# Define replacement rules
$replacements = @{
    # Field name mappings
    '\.dept_name\b' = '.name'
    '\bdept_name\b' = 'name'
    '\.dept_id\b' = '.id'
    '\bdept_id\b' = 'id'
    '\.parent_dept\b' = '.parent_department'
    '\bparent_dept\b' = 'parent_department'
    "order_by\('dept_name'\)" = "order_by('name')"
    "order_by\(`"dept_name`"\)" = "order_by(`"name`")"
    
    # Related name changes
    "Count\('employee'\)" = "Count('employees')"
    "employee__emp_status" = "employees__emp_status"
    "filter=Q\(employee__" = "filter=Q(employees__"
}

# Directories to process
$directories = @(
    'apps\hr',
    'apps\reports',
    'apps\inventory',
    'administrator',
    'org',
    'templates'
)

$fileCount = 0
$replacementCount = 0

foreach ($dir in $directories) {
    $fullPath = Join-Path $PSScriptRoot $dir
    
    if (Test-Path $fullPath) {
        Write-Host "Processing: $dir" -ForegroundColor Yellow
        
        # Get all Python and HTML files
        $files = Get-ChildItem -Path $fullPath -Recurse -Include *.py,*.html | Where-Object {
            $_.FullName -notmatch '__pycache__' -and $_.FullName -notmatch '\.pyc$'
        }
        
        foreach ($file in $files) {
            $content = Get-Content $file.FullName -Raw -Encoding UTF8
            $originalContent = $content
            
            foreach ($pattern in $replacements.Keys) {
                if ($content -match $pattern) {
                    $content = $content -replace $pattern, $replacements[$pattern]
                }
            }
            
            if ($content -ne $originalContent) {
                Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
                $fileCount++
                Write-Host "  Updated: $($file.Name)" -ForegroundColor Green
            }
        }
    }
}

Write-Host ""
Write-Host "=== Update Complete ===" -ForegroundColor Cyan
Write-Host "Files modified: $fileCount" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: Please review the changes and test thoroughly!" -ForegroundColor Red
