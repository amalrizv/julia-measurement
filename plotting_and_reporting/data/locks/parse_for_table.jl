
using DelimitedFiles
using Statistics

input = "filenames.txt"
filenames = readdlm(input)
nfiles = length(filenames)
println("lang,op,mean")
for i =1:nfiles
	lang = Array{String,1}(undef, 2)
	if startswith(filenames[i], "c")
		lang[1] = "cpp"
	else 
		lang[1] = "julia"
	end
	op_str =["mutex_lock","mutex_trylock","mutex_unlock","sem_down","sem_up","spin_lock","spin_trylock","spin_unlock"]
	for j = 1:length(op_str)
		if endswith(filenames[i], op_str[j]*".dat")
			lang[2] = op_str[j]
		end
	end
	arr = readdlm(filenames[i], comments=true, comment_char='#')
	mean_arr = mean(arr)
	println(lang[1]*","*lang[2]*" ,$mean_arr")
end
