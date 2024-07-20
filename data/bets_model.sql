/*****************************
USERS
******************************/
create table users(
    id integer primary key,
    name varchar(100) not null unique,
    email varchar(100) not null unique,
    password text,
    is_active boolean not null default 0,
    is_admin boolean not null default 0
    );

/*****************************
MATCHES & MATCHES_LIVE
******************************/
 create table matches(
     id integer primary key,
     match_date datetime not null,
     match_group character(1) not null, 
     team1 varchar(20) not null, 
     team2 varchar(20) not null, 
     team1_res smallint, 
     team2_res smallint,
     points_multiplier NUMERIC,
     insert_date datetime not null default(datetime())
     ); 

create table matches_live 
        as select * from matches;

/*****************************
USERS_MATCHES
******************************/
create table user_matches(
    user_id integer,
    match_id integer,
    match_date datetime not null,
    match_group character(1) not null, 
    team1 varchar(20) not null, 
    team2 varchar(20) not null, 
    team1_res smallint, 
    team2_res smallint,
    insert_date datetime not null default(datetime()),
    PRIMARY KEY (user_id, match_id) 
    ); 

/*****************************
VIEW v_user_matches
******************************/
--drop view v_user_matches;
create view v_user_matches as
select  
        um.user_id,
        u.name,
        um.match_id, 
        strftime('%d-%m-%Y %H:%M', um.match_date) as match_date, 
        um.match_group, 
        um.team1, 
        um.team2, 
        coalesce(um.team1_res,"-") as team1_res, 
        coalesce(um.team2_res,"-") as team2_res,
        case when um.match_date < strftime('%Y-%m-%d %H:%M:%S', datetime('now','+2 hour')) then "disabled" else "" end as disabled,
        m.team1_res as  team1_rres, 
        m.team2_res as  team2_rres,
        case
            when m.team1_res=m.team2_res and um.team1_res=um.team2_res and m.team1_res=um.team1_res then 6 * m.points_multiplier
            when m.team1_res=m.team2_res and um.team1_res=um.team2_res then 4 * m.points_multiplier
            else 0 
        end as points_draw,
        case 
            when m.team1_res!=m.team2_res and m.team1_res=um.team1_res and m.team2_res=um.team2_res then 6 * m.points_multiplier
            when m.team1_res!=m.team2_res and m.team1_res-m.team2_res = um.team1_res-um.team2_res then 4 * m.points_multiplier
            when ((m.team1_res>m.team2_res and um.team1_res>um.team2_res) or (m.team1_res<m.team2_res and um.team1_res<um.team2_res)) and (m.team1_res=um.team1_res or m.team2_res=um.team2_res) then 4 * m.points_multiplier
            when (m.team1_res>m.team2_res and um.team1_res>um.team2_res) or (m.team1_res<m.team2_res and um.team1_res<um.team2_res) then 3 * m.points_multiplier
            else 0 
        end as points_win,
        case 
            when (m.team1_res>m.team2_res and um.team1_res<=um.team2_res) and (m.team1_res=um.team1_res or m.team2_res=um.team2_res) then 1 * m.points_multiplier
            when (m.team1_res<m.team2_res and um.team1_res>=um.team2_res) and (m.team1_res=um.team1_res or m.team2_res=um.team2_res) then 1 * m.points_multiplier
            when (m.team1_res=m.team2_res and um.team1_res!=um.team2_res) and (m.team1_res=um.team1_res or m.team2_res=um.team2_res) then 1 * m.points_multiplier
            else 0
        end as points_lucky_loser,
        case 
            when (m.team1='Poland' or m.team2='Poland') --mecz Polski
                and (
                        (m.team1_res=m.team2_res and um.team1_res=um.team2_res) /*poprawnie wytypowany remis*/ 
                        or
                        ((m.team1_res>m.team2_res and um.team1_res>um.team2_res) or (m.team1_res<m.team2_res and um.team1_res<um.team2_res)) /*poprawnie wytypowane zwyciestwo/porazka*/ 
                    ) 
            then 5 * m.points_multiplier
            else 0
        end as points_bonus
        from user_matches um 
        left join matches m on um.match_id=m.id
        left join users u on um.user_id=u.id

/*****************************
VIEW v_rank
******************************/
create view v_rank as
select RANK () OVER (ORDER BY points DESC) as rank, r.nick, r.points 
from (
    select  u.name as nick, sum(points_draw + points_win + points_lucky_loser + points_bonus) as points
    from v_user_matches um inner join users u on um.user_id = u.id
    group by user_id
)  r

/*****************************
VIEW v_user_matches_live
******************************/
--drop view v_user_matches_live;
create view v_user_matches_live as
select  
        um.user_id,
        u.name,
        um.match_id, 
        strftime('%d-%m-%Y %H:%M', um.match_date) as match_date, 
        um.match_group, 
        um.team1, 
        um.team2, 
        coalesce(um.team1_res,"-") as team1_res, 
        coalesce(um.team2_res,"-") as team2_res,
        case when um.match_date < strftime('%Y-%m-%d %H:%M:%S', datetime('now','+2 hour')) then "disabled" else "" end as disabled,
        m.team1_res as  team1_rres, 
        m.team2_res as  team2_rres,
        case
            when (um.team1_res not between 0 and 9) or (m.team1_res not between 0 and 9) then 0 
            when m.team1_res=m.team2_res and um.team1_res=um.team2_res and m.team1_res=um.team1_res then 6 * m.points_multiplier
            when m.team1_res=m.team2_res and um.team1_res=um.team2_res then 4 * m.points_multiplier
            else 0 
        end as points_draw,
        case 
            when (um.team1_res not between 0 and 9) or (m.team1_res not between 0 and 9) then 0
            when m.team1_res!=m.team2_res and m.team1_res=um.team1_res and m.team2_res=um.team2_res then 6 * m.points_multiplier
            when m.team1_res!=m.team2_res and m.team1_res-m.team2_res = um.team1_res-um.team2_res then 4 * m.points_multiplier
            when ((m.team1_res>m.team2_res and um.team1_res>um.team2_res) or (m.team1_res<m.team2_res and um.team1_res<um.team2_res)) and (m.team1_res=um.team1_res or m.team2_res=um.team2_res) then 4 * m.points_multiplier
            when (m.team1_res>m.team2_res and um.team1_res>um.team2_res) or (m.team1_res<m.team2_res and um.team1_res<um.team2_res) then 3 * m.points_multiplier
            else 0 
        end as points_win,
        case
            when (um.team1_res not between 0 and 9) or (m.team1_res not between 0 and 9) then 0 
            when (m.team1_res>m.team2_res and um.team1_res<=um.team2_res) and (m.team1_res=um.team1_res or m.team2_res=um.team2_res) then 1 * m.points_multiplier
            when (m.team1_res<m.team2_res and um.team1_res>=um.team2_res) and (m.team1_res=um.team1_res or m.team2_res=um.team2_res) then 1 * m.points_multiplier
            when (m.team1_res=m.team2_res and um.team1_res!=um.team2_res) and (m.team1_res=um.team1_res or m.team2_res=um.team2_res) then 1 * m.points_multiplier
            else 0
        end as points_lucky_loser,
        case
            when (um.team1_res not between 0 and 9) or (m.team1_res not between 0 and 9) then 0 
            when (m.team1='Poland' or m.team2='Poland') --mecz Polski
                and (
                        (m.team1_res=m.team2_res and um.team1_res=um.team2_res) /*poprawnie wytypowany remis*/ 
                        or
                        ((m.team1_res>m.team2_res and um.team1_res>um.team2_res) or (m.team1_res<m.team2_res and um.team1_res<um.team2_res)) /*poprawnie wytypowane zwyciestwo/porazka*/ 
                    ) 
            then 5 * m.points_multiplier
            else 0
        end as points_bonus
        from user_matches um 
        left join matches_live m on um.match_id=m.id
        left join users u on um.user_id=u.id

/*****************************
VIEW v_rank_live
******************************/
create view v_rank_live as
select RANK () OVER (ORDER BY r.points + r.points_live DESC) as rank, r.nick, 
    r.points, r.points_live, r.points + r.points_live as points_total 
from (
    select  u.name as nick, 
        sum(um.points_draw + um.points_win + um.points_lucky_loser + um.points_bonus) as points,
        sum(l.points_draw + l.points_win + l.points_lucky_loser + l.points_bonus) as points_live
    from v_user_matches um 
        inner join users u on um.user_id = u.id
        left join (select * from v_user_matches_live where match_id not in (select id from matches where team1_res >=0)) l on um.user_id = l.user_id and um.match_id = l.match_id
    group by um.user_id
)  r