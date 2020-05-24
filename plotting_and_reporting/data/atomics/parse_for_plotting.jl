using DelimitedFiles
using Statistics

input = "filenames.txt"
filenames = readdlm(input)
nfiles = length(filenames)
println("lang,op,mean")
for i =1:nfiles
	if startswith(filenames[i], "c")
		lang = "CPP"
	else 
		lang = "Julia"
	end
	if endswith(filenames[i], "_set.dat")
		op = "set"
	elseif endswith(filenames[i], "_cas.dat")
		op = "cas"
	elseif endswith(filenames[i], "_add.dat")
		op = "add"
	elseif endswith(filenames[i], "_sub.dat")
		op = "sub"
	elseif endswith(filenames[i], "_or.dat")
		op = "or"
	elseif endswith(filenames[i], "_and.dat")
		op = "and"
	elseif endswith(filenames[i], "_nand.dat")
		op = "nand"
	else 
		break;
	end
	arr = readdlm(filenames[i], comments=true, comment_char='#')
	mean_file = mean(arr)
	println(lang*","*op*",$mean_file")
end
	
