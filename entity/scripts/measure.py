#!/usr/bin/python

import os, sys, csv

def main(argv):
    helpline = 'ontology.py <input> -c <code>'

    if len(argv) != 2:
        print helpline
        sys.exit(2)

    file1 = argv[0]
    file2 = argv[1]
        
    print "Measuring differences between ontologies..."
    print "\nFile1: " + os.path.split(file1)[1]
    matrix1 = read_ontology(file1)
    print_matrix(matrix1)
    
    print "\nFile2: " + os.path.split(file2)[1]
    matrix2 = read_ontology(file2)
    print_matrix(matrix2)

    unique1, unique2, shared = compare_matrices(matrix1, matrix2)
    print "Results: %s (%s-%s)" % (len(shared),len(unique1),len(unique2))

    print "\nShared"
    for x in shared:
        print x
        
    print "\nUnique1"
    for x in unique1:
        print x

    print "\nUnique2"
    for x in unique2:
        print x

    # compute fleiss' kappa on the shared items
    rated_items = []
    for item in shared:
        rated_items.append([item[0], 'rater1', item[1]])
        rated_items.append([item[0], 'rater2', item[2]])
    ratings = ['rel_s', 'rel_e', 'rel_p']
    p, p_e, k = compute_fleiss(rated_items, ratings)
    print "\nFleiss: p = %s, p_e = %s, k = %s" % (p, p_e, k)
        
def compare_matrices(matrix1, matrix2):
    unique1 = []
    unique2 = []
    shared = []
    for x in matrix1:
        if not x in matrix2:
            for y in matrix1[x]:
                if matrix1[x][y] != 'rel_e':
                    unique1.append([x, y, matrix1[x][y]])
        else:
            for y in matrix1[x]:
                if not y in matrix2[x] and matrix1[x][y] != 'rel_e':
                    unique1.append([x, y, matrix1[x][y]])
                else:
                    shared.append([x + ":" + y, matrix1[x][y], matrix2[x][y]])
    for x in matrix2:
        if not x in matrix1:
            for y in matrix2[x]:
                if matrix2[x][y] != 'rel_e':
                    unique2.append([x, y, matrix2[x][y]])
        else:
            for y in matrix2[x]:
                if not y in matrix1[x] and matrix2[x][y] != 'rel_e':
                    unique2.append([x, y, matrix2[x][y]])

    return unique1, unique2, shared
    
def read_ontology(filename):
    matrix = {}
    with open(filename, 'rU') as csvf:
        csvreader = csv.reader(csvf, delimiter=',', quotechar='"')
        headers = csvreader.next();
        # headers: parent_id, parent, child_id, child, relaton
        for [pid, parent, cid, child, rel] in csvreader:
            if not parent in matrix:
                matrix[parent] = {child : rel}
            elif child in matrix[parent]:
                print "Duplicate entry: %s, %s (%s and %s)" % (parent, child, rel, matrix[parent][child])
            else:
                matrix[parent][child] = rel

            # add a symmetric relation for equivalent
            if rel == "rel_e":
                matrix[child] = {parent : rel}
    return matrix

def print_matrix(matrix):
    for x in matrix:
        for y in matrix[x]:
            print "%s, %s (%s)" % (x, y, matrix[x][y])

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

if __name__ == "__main__":
    main(sys.argv[1:])
