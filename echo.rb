#!/usr/bin/env ruby

require 'json'

class EchoServer
    def initialize
        @node_id = nil
    end

    def main!
        while line = STDIN.gets
            req = JSON.parse(line, symbolize_names: true)
            STDERR.puts "Recv #{line.inspect}"

            body = req[:body]
            case body[:type]
            when 
        end
    end
end

EchoServer.new.main!