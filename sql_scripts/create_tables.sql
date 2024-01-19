CREATE TABLE public.cities (
	id serial4 NOT NULL,
	"name" varchar NULL,
	CONSTRAINT cities_pkey PRIMARY KEY (id)
);

CREATE TABLE public.users (
	id serial4 NOT NULL,
	username varchar NULL,
	profile_url varchar NULL,
	age int4 NULL,
	gender varchar NULL,
	city_id int4 NULL,
	interests varchar NULL,
	CONSTRAINT users_pkey PRIMARY KEY (id)
);

CREATE TABLE public.search_criteria (
	id serial4 NOT NULL,
	age_range varchar NULL,
	gender_preference varchar NULL,
	city_id int4 NULL,
	interests varchar NULL,
	CONSTRAINT search_criteria_pkey PRIMARY KEY (id)
);

ALTER TABLE public.search_criteria ADD CONSTRAINT search_criteria_city_id_fkey FOREIGN KEY (city_id) REFERENCES public.cities(id);

CREATE TABLE public.user_searches (
	id serial4 NOT NULL,
	user_id int4 NULL,
	"timestamp" timestamp NULL,
	criteria_id int4 NULL,
	CONSTRAINT user_searches_pkey PRIMARY KEY (id)
);

ALTER TABLE public.user_searches ADD CONSTRAINT user_searches_criteria_id_fkey FOREIGN KEY (criteria_id) REFERENCES public.search_criteria(id);
ALTER TABLE public.user_searches ADD CONSTRAINT user_searches_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);

CREATE TABLE public.favorites (
	id serial4 NOT NULL,
	user_id int4 NULL,
	favorite_user_id int4 NULL,
	CONSTRAINT favorites_pkey PRIMARY KEY (id)
);

ALTER TABLE public.favorites ADD CONSTRAINT favorites_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);

CREATE TABLE public.match_results (
	id serial4 NOT NULL,
	search_id int4 NULL,
	matched_user_id int4 NULL,
	CONSTRAINT match_results_pkey PRIMARY KEY (id)
);

ALTER TABLE public.match_results ADD CONSTRAINT match_results_search_id_fkey FOREIGN KEY (search_id) REFERENCES public.user_searches(id);

CREATE TABLE public.user_search_results (
	id serial4 NOT NULL,
	search_id int4 NULL,
	found_user_id int4 NULL,
	CONSTRAINT user_search_results_pkey PRIMARY KEY (id)
);
ALTER TABLE public.user_search_results ADD CONSTRAINT user_search_results_search_id_fkey FOREIGN KEY (search_id) REFERENCES public.user_searches(id);


