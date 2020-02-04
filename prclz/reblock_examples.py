from i_reblock import reblock_gadm


#reblock_gadm(region, gadm_code, gadm, simplify, block_list=None, only_block_list=False, drop_already_completed=True)


def reblock_block_list(block_list, region):

	gadm_list = [s[0:s.rfind("_")] for s in block_list]
	gadm_code = gadm_list[0][0:3]
	for gadm, block in zip(gadm_list, block_list):

		reblock_gadm(region, gadm_code, [gadm], simplify, block_list=[block], only_block_list=True, drop_already_completed=True)


nairobi = ['KEN.30.3.3_1_59', 'KEN.30.17.4_1_63', 'KEN.30.10.2_1_27', 'KEN.30.16.1_1_3']
kathmandu = ['NPL.1.1.3.31_1_343', 'NPL.1.1.3.14_1_68', 'NPL.1.1.3.31_1_3938', 'NPL.1.1.3.31_1_1253']
monrovia = ['LBR.11.2.1_1_2563', 'LBR.11.2.1_1_282', 'LBR.11.2.1_1_1360', 'LBR.11.2.1_1_271']

regions = ['Africa', 'Asia', 'Africa']
block_aois = [nairobi, kathmandu, monrovia]

for b, r in zip(block_aois, regions):

	print("\n\n Working on {}".format(b[0][0:3]))
	reblock_block_list(b, r)