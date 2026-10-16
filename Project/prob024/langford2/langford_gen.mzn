include "alldifferent.mzn";
include "global_cardinality.mzn";
include "lex_lesseq.mzn";

% data from proj.py
int: n;                 % numbers 1..n
int: s;                 % copies per number (s=2 is classic Langford)
int: d;                 % consecutive copies of i are i+d apart (d=1 Langford, d=0 Nickerson)
int: search_mode;       % 0..3, see solve item
bool: use_gcc;          % redundant: each number occurs exactly s times
bool: use_parity_cut;   % redundant: parity argument (only used when s=2, d=1)
bool: break_symmetry;   % reversal symmetry

int: N = s * n;
set of int: NUMS = 1..n;
set of int: POS  = 1..N;

% p[i] = position of the FIRST copy of i
array[NUMS] of var POS: p;
% seq[q] = number at position q (determined by p, kept for output/channelling)
array[POS] of var NUMS: seq;

% the last copy must fit in the sequence
constraint forall(i in NUMS)( p[i] + (s-1)*(i+d) <= N );

% no two copies share a position
constraint all_different([ p[i] + j*(i+d) | i in NUMS, j in 0..s-1 ]);

% channelling p -> seq
constraint forall(i in NUMS, j in 0..s-1)( seq[p[i] + j*(i+d)] = i );

% every number appears exactly s times
constraint if use_gcc then
  global_cardinality(seq, [i | i in NUMS], [s | i in NUMS])
else true endif;

% keep only one of a sequence and its reverse.
% Reversing moves the first copy of i to N+1 - (s-1)*(i+d) - p[i]. 
array[NUMS] of var int: p_rev = [ N+1 - (s-1)*(i+d) - p[i] | i in NUMS ];
constraint if break_symmetry then
  if search_mode < 2 then lex_lesseq(p, p_rev)
  else lex_lesseq([ p[n+1-i] | i in NUMS ], [ p_rev[n+1-i] | i in NUMS ]) endif
else true endif;

% redundant, from the parity argument (s=2, d=1 only):
% odd i has even spacing, so both copies have the same parity. The odd numbers
% must fill the odd positions left over by the even numbers, in pairs.
constraint if use_parity_cut /\ s = 2 /\ d = 1 then
  if ((n+1) div 2) mod 2 = 0 then
    sum(i in NUMS where i mod 2 = 1)( bool2int(p[i] mod 2 = 1) ) = ((n+1) div 2) div 2
  else false endif
else true endif;

% 0/1 = natural order, 2/3 = largest number first
array[NUMS] of var POS: p_desc = [ p[n+1-i] | i in NUMS ];
solve :: ( if   search_mode = 0 then int_search(p,      input_order, indomain_min)
           elseif search_mode = 1 then int_search(p,      first_fail,  indomain_min)
           elseif search_mode = 2 then int_search(p_desc, input_order, indomain_min)
           else                        int_search(p_desc, first_fail,  indomain_min)
           endif ) satisfy;
% Python package reads the variables directly.