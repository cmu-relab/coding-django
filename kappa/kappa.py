#!/usr/bin/python

import sys, csv

def main(argv):
    if len(argv) == 0:
        print 'kappa.py <input1> [input2]\n'
        exit()

    print_kappa(argv[0])

    if len(argv) == 2:
        datafile1 = open(argv[0], 'r').read().splitlines()
        raters1, codes1, items1, coded_items1 = read_items(datafile1)

        print_kappa(argv[1])
        datafile2 = open(argv[1], 'r').read().splitlines()
        raters2, codes2, items2, coded_items2 = read_items(datafile2)

        # vanbelle's assumes same codes for both datasets
        codes = list(set(codes1) | set(codes2))
        n1, p_ij1, p_j1 = compute_response_table(coded_items1, codes)
        n2, p_ij2, p_j2 = compute_response_table(coded_items2, codes)

        if n1 != n2:
            print "Unequal number of items between groups: %s != %s" % (n1, n2)
            exit(0)

        p_o, p_e, p_m, k = compute_vanbelle(n1, p_ij1, p_j1, p_ij2, p_j2)
        print "\nVanbelle's Kappa:"
        print "N = %s" % n1
        print "P_o = %s" % p_o
        print "P_e = %s" % p_e
        print "P_m = %s" % p_m
        print "K = %s" % k

def print_kappa(datafile):
    print "\nInput File: %s" % datafile

    datafile = open(datafile, 'r').read().splitlines()
    raters, codes, items, coded_items = read_items(datafile)
    p, p_e, k = compute_fleiss(coded_items, codes)
    var, bias = compute_jackknife(coded_items, codes)
    n = len(items)

    print "\nFleiss' Kappa:"
    print "N = %s" % n
    print "P = %s" % p
    print "P_e = %s" % p_e
    print "K = %s" % k
    print "var = %s" % var
    print "bias = %s" % bias

    if len(raters) == 2:
        p_o, p_e, k = compute_cohens(raters, coded_items, codes)
        print "\nCohen's Kappa:"
        print "N = %s" % n
        print "P_o = %s" % p_o
        print "P_e = %s" % p_e
        print "K = %s" % k
    return

def compute_vanbelle(n, p_ij1, p_j1, p_ij2, p_j2):

    # compute the observed proportion of agreement
    p_o = 0
    for item in p_ij1:
        for rating in p_ij1[item]:
            p_o += p_ij1[item][rating] * p_ij2[item][rating]
    p_o = p_o / n

    # compute the proportion of agreement expected by chance
    p_e = 0
    for rating in p_j1:
        p_e += p_j1[rating] * p_j2[rating]

    # compute the maximum proportion of observed agreement
    p_m = 0
    for item in p_ij1:
        sum1 = sum([x * x for x in p_ij1[item].values()])
        sum2 = sum([x * x for x in p_ij2[item].values()])
        p_m += max(sum1, sum2)
    p_m = p_m / n

    # compute VanBelle's agreement index
    if p_o == 1.0 and p_e == 1.0 and p_m == 1.0:
        k = 0.0
    else:
        k = ((p_o - p_e) / (p_m - p_e))
    return p_o, p_e, p_m, k

def compute_cohens(raters, rated_items, ratings):
    if len(raters) != 2:
        return 0, 0, 0

    # pair ratings by item and index by rater
    index = {raters[0]: 0, raters[1]: 1}
    item_table = {}
    for [item, rater, rating] in rated_items:
        if item not in item_table:
            item_table[item] = ["", ""]
        item_table[item][index[rater]] = rating

    # compute the 2x2 contigency table by category
    cont_table = [[0 for x in ratings] for y in ratings]
    for item in item_table:
        x = ratings.index(item_table[item][0])
        y = ratings.index(item_table[item][1])
        cont_table[x][y] += 1

    n = len(item_table)
    p_o = 0.0
    p_e = 0.0
    for j in range(0, len(cont_table)):
        p_o += float(cont_table[j][j]) / n
        p_e += float(cont_table[j][j] * cont_table[j][j]) / (n * n)

    k = (p_o - p_e) / (1.0 - p_e)
    return p_o, p_e, k    

def compute_fleiss(rated_items, ratings):
    rating_matrix = {}
    raters = []
    p_i = {}
    p_j = {x:0 for x in ratings}
    n = 0
    
    # compute the rating sum per item
    for [item, rater, rating] in rated_items:
        if not item in rating_matrix:
            rating_matrix[item] = {x:0 for x in ratings}
            p_i[item] = 0
        rating_matrix[item][rating] += 1
        p_j[rating] += 1
        n += 1
        if not rater in raters:
            raters.append(rater)

    total_raters = len(raters)
    for item in p_i:
        p_i[item] = (float(1) / (total_raters * (total_raters - 1))) * (sum([rating_matrix[item][x] * rating_matrix[item][x] for x in rating_matrix[item]]) - total_raters)

    for rating in ratings:
        p_j[rating] = float(p_j[rating]) / n

    # compute Fleiss' agreement index
    p = (float(1) / len(p_i.keys())) * sum([x for x in p_i.values()])
    p_e = sum([x * x for x in p_j.values()])
    if p_e != 1.0:
        k = (p - p_e) / (float(1) - p_e)
    else:
        k = 0.0

    return p, p_e, k

def compute_jackknife(rated_items, ratings):
    N, p_ij, p_j = compute_response_table(rated_items, ratings)
    p, p_e, k_N = compute_fleiss(rated_items, ratings)

    k_N_i = [0 for x in rated_items]
    k_N_est = 0.0

    for x in range(0, len(rated_items)):
        # python function to yield list without an element?
        rated_items_1 = rated_items[0:x]
        rated_items_1.extend(rated_items[x + 1:])
        p, p_e, k_N_i_1 = compute_fleiss(rated_items_1, ratings)
        k_N_i[x] = (N * k_N) - ((N - 1) * k_N_i_1)
        k_N_est += k_N_i[x]

    k_N_est /= N
    var_k_N = 0.0
    for x in k_N_i:
        var_k_N += (x - k_N) * (x - k_N)
    var = var_k_N * (1.0 / (N - 1)) * (1.0 / N)
    bias = (N - 1) * (k_N_est - k_N)

    return var, bias

def read_items(datafile):
    csvreader = csv.reader(datafile, delimiter=',', quotechar='"')
    codes = {}
    items = {}
    coded_items = []
    raters = csvreader.next();

    for row in csvreader:
        for i in range(1, len(row)):
            coded_items.append([row[0], raters[i], row[i]])
            codes[row[i]] = 1
            items[row[0]] = 1

    # strip first element, which is item column
    raters = raters[1:]
    return raters, codes.keys(), items.keys(), coded_items

def compute_response_table(rated_items, ratings, normalize=True):
    total_ratings = 0
    p_ij = {} # the proportions of raters classifying item by category
    p_j = {x:0 for x in ratings} # marginal classification distributions

    for [item, rater, rating] in rated_items:

        # compute the probability over the population of raters that
        # a rater classifies item in category rating
        if not item in p_ij:
            p_ij[item] = {x:0 for x in ratings}
        
        p_ij[item][rating] += 1
        p_j[rating] += 1
        total_ratings += 1

    if not normalize:
        return len(p_ij.keys()), p_ij, p_j

    # normalize p_i by the total number of raters per item
    for item in p_ij:
        item_ratings = 0
        for rating in p_ij[item]:
            item_ratings += p_ij[item][rating]
        for rating in p_ij[item]:
            p_ij[item][rating] = float(p_ij[item][rating]) / item_ratings
        #print "item: %s p_i,j = %s" % (item, p_ij[item])

    # normalize p_j by the total number of ratings
    for rating in p_j:
        p_j[rating] = float(p_j[rating]) / total_ratings
        #print "rating: %s p_j = %s" % (rating, p_j[rating])

    return len(p_ij.keys()), p_ij, p_j

def print_response_table(p_ij, p_j, codes):
    print "Item\t%s" % "\t".join(codes)
    for item in sorted(p_ij.keys()):
        print "%s\t%s" % (item, "\t".join([("%.2f" % p_ij[item][x]) for x in codes]))
    print "p_j\t%s" % "\t".join([("%.2f" % p_j[x]) for x in codes])


if __name__ == "__main__":
    main(sys.argv[1:])
