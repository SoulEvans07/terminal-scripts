import groovy.io.FileType

if(args.length != 1){
	System.out.println("Usage: wheris [command|file]")
	return;
}

System.out.println("searching for " + args[0]);

String path = System.getenv("Path");
path.split(";").each{line -> 
	if(line.trim().length() > 0){
		def dir = new File(line);
		dir.eachFile (FileType.FILES) { file -> 
			def fapath = file.getAbsolutePath();
			def ext = fapath.lastIndexOf(".");
			def sep = fapath.lastIndexOf(System.getProperty("file.separator"));
			if(ext > 0 && sep > 0 && sep < ext){
				fapath = fapath.substring(0, ext);
			}
			if(fapath.endsWith(args[0])){
				System.out.println(file);
			}
		}
	}
};
//System.out.println(path);
//System.out.println(args[0]);