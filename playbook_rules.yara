rule scan_anonymous_ftp {
    meta:
        author = "Cole Daubenspeck"
        updated = "20191027"
        description = "When FTP is on target and on port 22, checks for anonymous login (high/critical finding)"
        module = "scan_anon_ftp"
    strings:
        $port = /\[[0-9]+\].port = 22/
        $service = /\[[0-9]+\].service = .*ftp.*/ nocase
    condition:
        all of them
}
rule grab_ftp_file_list {
    meta:
        author = "Cole Daubenspeck"
        updated = "20191031"
        description = "Get a list of files on the anonymous FTP server"
        module = "grab_ftp_file_list"
    strings:
        $vuln = "Anonymous FTP Login"
    condition:
        all of them
}