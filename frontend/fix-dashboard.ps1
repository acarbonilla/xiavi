# Add missing Quick Actions to dashboard
$filePath = "app\dashboard\page.tsx"
$content = Get-Content $filePath -Raw

# Add missing imports
$content = $content -replace 'BarChart3\r\n\} from', @'
BarChart3,
    Briefcase,
    BookOpen
} from
'@

# Add missing Quick Actions (after View Progress link)
$content = $content -replace '(\s+<span className="text-sm font-medium text-gray-900">View Progress</span>\r\n\s+</Link>)\r\n(\s+</div>)', @'
$1
                                <Link href="/scenarios" className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                                    <Briefcase className="w-5 h-5 text-gray-600" />
                                    <span className="text-sm font-medium text-gray-900">Practice Scenarios</span>
                                </Link>
                                <Link href="/vocabulary" className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                                    <BookOpen className="w-5 h-5 text-gray-600" />
                                    <span className="text-sm font-medium text-gray-900">Vocabulary Builder</span>
                                </Link>
                                <Link href="/resume" className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                                    <Clock className="w-5 h-5 text-gray-600" />
                                    <span className="text-sm font-medium text-gray-900">Resume Conversations</span>
                                </Link>
$2
'@

$content | Set-Content $filePath -NoNewline
Write-Host "Dashboard updated successfully!"
